from django.shortcuts import redirect
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from base64 import b64decode
import re

from . import models, forms

def send_message(author, receiver, conversation, text, in_response_to=None):
    message = models.Message.objects.create(
        author=author,
        conversation=conversation,
        text=text,
        in_response_to=in_response_to)
    notify_about_new_message(author.user,
                             receiver.user,
                             conversation.item,
                             text,
                             message.id)

@login_required
def send_intro_message(request):
    author = request.user.profile
    item = models.Item.objects.get(pk=request.POST['item'])
    to = item.item_seller_name
    text = request.POST['message']
    conversation = models.Conversation.objects.create(
        item=item,
        buyer=author,
    )
    send_message(author, to, conversation, text)
    return redirect(reverse('marketplace:message_list',
                            args=[item.pk]))


def notify_about_new_message(sender, receiver, item, message, uuid):
    name = f"{sender.first_name} {sender.last_name}"
    subject = f"New message about {item.item_name} from {name}"
    html_message = render_to_string('marketplace/notification_email.html',
                                    {
                                        'message': message,
                                        'item': item,
                                        'name': name,
                                    })
    message = mail.EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),
        to=[receiver.email],
        reply_to=[f'{settings.CLOUDMAILIN_ID}+{uuid}@cloudmailin.net'],
    )
    message.attach_alternative(html_message, "text/html")
    message.send()

@csrf_exempt
def receive_message(request):
    if is_unauthorized(request):
        return HttpResponse(status=403)
    f = forms.ReceiveMessageForm(rename_fields(request.POST))
    if not f.is_valid():
        return HttpResponse(status=400, reason="Failed to validate form")
    message = f.save()
    receiver = other_participant(message.conversation, message.author)
    notify_about_new_message(sender=message.author.user,
                             receiver=receiver.user,
                             item=message.conversation.item,
                             message=message.text,
                             uuid=message.id)
    return HttpResponse(status=200)

def other_participant(conversation, person_a):
    if conversation.buyer == person_a:
        return conversation.item.item_seller_name
    else:
        return conversation.buyer

def rename_fields(post):
    return {
        'in_response_to': post['headers[To]'],
        'author': post['headers[From]'],
        'text': post['reply_plain'] or post['plain'],
    }

def is_unauthorized(request):
    if not 'authorization' in request.headers:
        return True
    authorization_re = re.compile(r'Basic (.+)')
    authorization = authorization_re.search(request.headers['authorization'])
    if not authorization:
        return True
    authorization = b64decode(authorization.group(1)).decode('ascii')
    return (authorization is None or
            authorization != settings.CLOUDMAILIN_CREDENTIALS)

class ConversationView(LoginRequiredMixin, generic.ListView):
    model=models.Conversation

    def get_queryset(self):
        return self.model.objects.filter(
            # only return conversation that are
            # 1) about this item, and
            # 2) involving this user as either buyer or seller
            Q(item__pk=self.kwargs['pk'])
            & (Q(buyer=self.request.user.profile) 
              | Q(item__item_seller_name=self.request.user.profile))
           )
    
    def get_context_data(self):
        context = super().get_context_data()
        conversation_list = []
        for conversation_obj in context['object_list']:
            conversation = {}
            to = other_participant(conversation_obj, self.request.user.profile)
            conversation['to'] = to
            conversation['form'] = forms.SendMessageForm(
                initial={
                    'to': to,
                    'item': conversation_obj.item,
                    'conversation': conversation_obj,
                    'in_response_to': conversation_obj.message_set.order_by('date').last()
                }
            )
            conversation['conversation'] = conversation_obj
            conversation_list.append(conversation)
        context['conversation_list'] = conversation_list
        context['item'] = models.Item.objects.get(pk=self.kwargs['pk'])
        return context
    
    def post(self, request, pk):
        form = forms.SendMessageForm(request.POST)
        if form.is_valid():
            send_message(author=request.user.profile,
                         receiver=form.cleaned_data['to'],
                         conversation=form.cleaned_data['conversation'],
                         in_response_to=form.cleaned_data['in_response_to'],
                         text=form.cleaned_data['text'])
        return self.get(request)
