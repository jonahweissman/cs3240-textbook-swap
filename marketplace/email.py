from django.shortcuts import redirect
from django.core import mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from email.errors import MessageParseError
from base64 import b64decode
import re

from . import models

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
    # parse authorization
    authorization_re = re.compile(r'Basic (.+)')
    authorization = authorization_re.search(request.headers['authorization'])
    if authorization is None or b64decode(authorization.group(1)).decode('ascii') != settings.CLOUDMAILIN_CREDENTIALS:
        return HttpResponse(status=403)
    # parse sender email
    email_re = re.compile(r'<(.+@.+\..+)>')
    email = email_re.search(request.POST['headers[From]'])
    if email is None:
        raise MessageParseError
    email = email.group(1)
    from_user = models.User.objects.filter(email=email)[0]
    # parse tracking uuid
    uuid_re = re.compile(r'\+(.*)@')
    uuid = uuid_re.search(request.POST['headers[To]'])
    if uuid is None:
        raise MessageParseError
    uuid = uuid.group(1)
    # parse content
    text = request.POST.get('reply_plain') or request.POST.get('plain')
    # save to DB
    in_response_to = models.Message.objects.get(pk=uuid)
    conversation = in_response_to.conversation
    message = models.Message(
        author=from_user.profile,
        in_response_to=in_response_to,
        conversation=conversation,
        text=text)
    message.save()
    if conversation.buyer == from_user.profile:
        to = conversation.item.item_seller_name.user
    else:
        to = conversation.buyer.user
    notify_about_new_message(from_user, to, conversation.item, text, message.id)
    return HttpResponse(status=200)

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
