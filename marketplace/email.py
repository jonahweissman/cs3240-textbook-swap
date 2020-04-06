from django.shortcuts import redirect
from django.core import mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from email.errors import MessageParseError
from base64 import b64decode
import re
from uuid import uuid4
import os

from . import models

@login_required
def send_intro_message(request):
    item = models.Item.objects.get(pk=request.POST['item'])
    to = item.item_seller_name.user.email
    name = f"{request.user.first_name} {request.user.last_name}"
    subject = f"A message about {item.item_name}"
    body = f"Hi I'm {name} and I'd like to buy {item.item_name}"
    uuid = uuid4()
    message = mail.EmailMessage(
        subject=subject,
        body=body,
        to=[to],
        reply_to=['8becc54808c611029b55+%s@cloudmailin.net' % uuid],
    )
    message.send()
    new_conversation = models.Conversation.objects.create(
        item=item,
        buyer=request.user.profile,
    )
    message = models.Message(
        author=request.user.profile,
        conversation=new_conversation,
        id=uuid,
        text=body)
    message.save()
    return redirect(reverse('marketplace:message_list',
                            args=[item.pk]))

@csrf_exempt
def receive_message(request):
    authorization_re = re.compile(r'Basic (.+)')
    authorization = authorization_re.search(request.headers['authorization'])
    if authorization is None or b64decode(authorization.group(1)).decode('ascii') != settings.CLOUDMAILIN_CREDENTIALS:
        return HttpResponse(status=403)
    email_re = re.compile(r'<(.+@.+\..+)>')
    email = email_re.search(request.POST['headers[From]'])
    if email is None:
        raise MessageParseError
    email = email.group(1)
    from_user = models.User.objects.filter(email=email)[0]
    uuid_re = re.compile(r'\+(.*)@')
    uuid = uuid_re.search(request.POST['headers[To]'])
    if uuid is None:
        raise MessageParseError
    uuid = uuid.group(1)
    text = request.POST.get('reply_plain') or request.POST.get('plain') or request.POST.get('html')
    message = models.Message(
        author=models.Profile.objects.get(pk=from_user),
        in_response_to=models.Message.objects.get(pk=uuid),
        conversation=models.Message.objects.get(pk=uuid).conversation,
        text=text)
    message.save()
    return HttpResponse(status=200)

class ConversationView(generic.ListView):
    model=models.Message

    def get_queryset(self):
        print(self.kwargs)
        return self.model.objects.filter(
            Q(conversation__item__pk=self.kwargs['pk'])
        )
