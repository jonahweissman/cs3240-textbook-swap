from django.shortcuts import redirect
from django.core import mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, QueryDict
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from base64 import b64decode
import re

from . import models, forms

@login_required
def send_intro_message(request):
    item = models.Item.objects.get(pk=request.POST['item'])
    to = item.item_seller_name.user
    text = request.POST['message']
    message = models.Message.objects.create(
        author=request.user.profile,
        conversation=models.Conversation.objects.create(
            item=item,
            buyer=request.user.profile,
        ),
        text=text)
    notify_about_new_message(request.user, to, item, text, message.id)
    return redirect(reverse('marketplace:message_list',
                            args=[item.pk]))

def notify_about_new_message(sender, receiver, item, message, uuid):
    name = f"{sender.first_name} {sender.last_name}"
    subject = f"New message about {item.item_name} from {name}"
    body = (f"{name} just sent you a message about {item.item_name}. "
            "Reply directly to this email to respond.\n"
            f"{'-' * 20}"
            "\n\n"
            f"{message}"
    )
    message = mail.EmailMessage(
        subject=subject,
        body=body,
        to=[receiver.email],
        reply_to=[f'{settings.CLOUDMAILIN_ID}+{uuid}@cloudmailin.net'],
    )
    message.send()

@csrf_exempt
def receive_message(request):
    if is_not_authorized(request):
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
    post = post.copy()
    post['in_response_to'] = post['headers[To]']
    post['author'] = post['headers[From]']
    post['text'] = post['reply_plain'] or post['plain']
    return post

def is_not_authorized(request):
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
