from django.contrib import admin
from .models import (
    Job,
    Application,
    EmailLog,
    AIInterviewSession,
    AIQuestion,
    AIAnswer,
    CallLog
)

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(EmailLog)

admin.site.register(AIInterviewSession)
admin.site.register(AIQuestion)
admin.site.register(AIAnswer)
admin.site.register(CallLog)
