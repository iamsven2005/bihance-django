from django.db import models


class Employerprofile(models.Model):
    id = models.TextField(primary_key=True)
    userid = models.OneToOneField(
        "User", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    companyname = models.TextField(
        db_column="companyName", blank=True, null=True
    )  # Field name made lowercase.
    companywebsite = models.TextField(
        db_column="companyWebsite", blank=True, null=True
    )  # Field name made lowercase.
    contactname = models.TextField(
        db_column="contactName", blank=True, null=True
    )  # Field name made lowercase.
    contactrole = models.TextField(
        db_column="contactRole", blank=True, null=True
    )  # Field name made lowercase.
    companysize = models.TextField(
        db_column="companySize", blank=True, null=True
    )  # Field name made lowercase.
    industry = models.TextField(blank=True, null=True)
    talentneeds = models.TextField(
        db_column="talentNeeds", blank=True, null=True
    )  # Field name made lowercase. This field type is a guess.

    workstyle = models.TextField(
        db_column="workStyle", blank=True, null=True
    )  # Field name made lowercase. This field type is a guess.

    hiringtimeline = models.TextField(
        db_column="hiringTimeline", blank=True, null=True
    )  # Field name made lowercase.
    featuredpartner = models.BooleanField(
        db_column="featuredPartner"
    )  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.
    image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "EmployerProfile"


class File(models.Model):
    id = models.TextField(primary_key=True)
    file_key = models.TextField()
    file_name = models.TextField()
    userid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "File"


class Job(models.Model):
    jobid = models.TextField(
        db_column="jobId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField(db_column="Name")  # Field name made lowercase.
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    startdate = models.DateTimeField(
        db_column="StartDate"
    )  # Field name made lowercase.
    enddate = models.DateTimeField(
        db_column="EndDate", blank=True, null=True
    )  # Field name made lowercase.
    salary = models.FloatField(
        db_column="Salary", blank=True, null=True
    )  # Field name made lowercase.
    highersalary = models.FloatField(
        db_column="HigherSalary", blank=True, null=True
    )  # Field name made lowercase.
    description = models.TextField(
        db_column="Description"
    )  # Field name made lowercase.
    requirements = models.TextField(
        db_column="Requirements", blank=True, null=True
    )  # Field name made lowercase.
    posteddate = models.DateTimeField(
        db_column="PostedDate"
    )  # Field name made lowercase.
    photourl = models.TextField(db_column="PhotoUrl")  # Field name made lowercase.
    startage = models.IntegerField(
        db_column="Startage", blank=True, null=True
    )  # Field name made lowercase.
    endage = models.IntegerField(
        db_column="Endage", blank=True, null=True
    )  # Field name made lowercase.
    gender = models.BooleanField(
        db_column="Gender", blank=True, null=True
    )  # Field name made lowercase.
    location = models.JSONField(blank=True, null=True)
    jobtype = models.TextField(
        db_column="jobType", blank=True, null=True
    )  # Field name made lowercase. This field type is a guess.
    locationname = models.TextField(
        db_column="locationName", blank=True, null=True
    )  # Field name made lowercase.
    company = models.TextField(
        db_column="Company", blank=True, null=True
    )  # Field name made lowercase.
    duration = models.TextField(
        db_column="Duration", blank=True, null=True
    )  # Field name made lowercase.
    paytype = models.TextField(
        db_column="PayType", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Job"


class Stripesubscription(models.Model):
    id = models.TextField(primary_key=True)
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    userid = models.OneToOneField(
        "User", models.DO_NOTHING, db_column="userId", blank=True, null=True
    )  # Field name made lowercase.
    subscriptionid = models.TextField(
        db_column="subscriptionId", unique=True, blank=True, null=True
    )  # Field name made lowercase.
    productid = models.TextField(
        db_column="productId", blank=True, null=True
    )  # Field name made lowercase.
    priceid = models.TextField(
        db_column="priceId", blank=True, null=True
    )  # Field name made lowercase.
    customerid = models.TextField(
        db_column="customerId", blank=True, null=True
    )  # Field name made lowercase.
    currentperiodend = models.DateTimeField(
        db_column="currentPeriodEnd"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "StripeSubscription"


class Suggestion(models.Model):
    id = models.TextField(primary_key=True)
    title = models.TextField()
    content = models.TextField()
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.
    authorid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="authorId"
    )  # Field name made lowercase.
    isuseful = models.BooleanField(db_column="isUseful")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "Suggestion"


class Suggestioncomment(models.Model):
    id = models.TextField(primary_key=True)
    content = models.TextField()
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.
    authorid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="authorId"
    )  # Field name made lowercase.
    suggestionid = models.ForeignKey(
        Suggestion, models.DO_NOTHING, db_column="suggestionId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "SuggestionComment"


class Suggestionvote(models.Model):
    id = models.TextField(primary_key=True)
    userid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    suggestionid = models.ForeignKey(
        Suggestion, models.DO_NOTHING, db_column="suggestionId"
    )  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "SuggestionVote"
        unique_together = (("userid", "suggestionid"),)


class Application(models.Model):
    applicationid = models.TextField(
        db_column="applicationId", primary_key=True
    )  # Field name made lowercase.
    jobid = models.ForeignKey(
        Job, models.DO_NOTHING, db_column="jobId"
    )  # Field name made lowercase.
    accept = models.IntegerField()
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    bio = models.TextField(
        db_column="Bio", blank=True, null=True
    )  # Field name made lowercase.
    employeereview = models.TextField(
        db_column="EmployeeReview", blank=True, null=True
    )  # Field name made lowercase.
    employerreview = models.TextField(
        db_column="EmployerReview", blank=True, null=True
    )  # Field name made lowercase.
    employerid = models.TextField(
        db_column="employerId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "application"


class ApplicationsApplication(models.Model):
    application_id = models.CharField(primary_key=True, max_length=36)
    accept = models.IntegerField()
    bio = models.TextField(blank=True, null=True)
    employee_review = models.TextField(blank=True, null=True)
    employer_review = models.TextField(blank=True, null=True)
    employer_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey("ApplicationsUser", models.DO_NOTHING)
    job = models.ForeignKey("ApplicationsJob", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "applications_application"


class ApplicationsJob(models.Model):
    job_id = models.CharField(primary_key=True, max_length=36)
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    salary = models.FloatField(blank=True, null=True)
    higher_salary = models.FloatField(blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    posted_date = models.DateTimeField()
    photo_url = models.CharField(max_length=200)
    start_age = models.IntegerField(blank=True, null=True)
    end_age = models.IntegerField(blank=True, null=True)
    gender = models.BooleanField(blank=True, null=True)
    location = models.JSONField(blank=True, null=True)
    job_type = models.CharField(max_length=20, blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=255, blank=True, null=True)
    pay_type = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey("ApplicationsUser", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "applications_job"


class ApplicationsUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    id = models.CharField(primary_key=True, max_length=36)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=254)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=20, blank=True, null=True)
    employee = models.BooleanField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    role = models.CharField(max_length=10)
    location = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "applications_user"


class ApplicationsUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(ApplicationsUser, models.DO_NOTHING)
    group = models.ForeignKey("AuthGroup", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "applications_user_groups"
        unique_together = (("user", "group"),)


class ApplicationsUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(ApplicationsUser, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "applications_user_user_permissions"
        unique_together = (("user", "permission"),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class Companyfollow(models.Model):
    id = models.TextField(primary_key=True)
    userid = models.TextField(db_column="userId")  # Field name made lowercase.
    companyid = models.TextField(db_column="companyId")  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "companyFollow"
        unique_together = (("userid", "companyid"),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(ApplicationsUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class Document(models.Model):
    documentid = models.TextField(
        db_column="documentId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField()
    description = models.TextField()
    url = models.TextField()
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")

    class Meta:
        managed = False
        db_table = "document"


class Group(models.Model):
    groupid = models.TextField(
        db_column="groupId", primary_key=True
    )  # Field name made lowercase.
    bio = models.TextField()
    creatorid = models.TextField(db_column="creatorId")  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "group"


class Groupmessage(models.Model):
    id = models.TextField(primary_key=True)
    content = models.TextField()
    groupid = models.ForeignKey(
        Group, models.DO_NOTHING, db_column="groupId"
    )  # Field name made lowercase.
    senderid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="senderId"
    )  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    isedited = models.BooleanField(db_column="isEdited")  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column="isDeleted")  # Field name made lowercase.
    lasteditedat = models.DateTimeField(
        db_column="lastEditedAt", blank=True, null=True
    )  # Field name made lowercase.
    replytoid = models.ForeignKey(
        "self", models.DO_NOTHING, db_column="replyToId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "groupMessage"


class Groupmessagefile(models.Model):
    id = models.TextField(primary_key=True)
    messageid = models.ForeignKey(
        Groupmessage, models.DO_NOTHING, db_column="messageId"
    )  # Field name made lowercase.
    userid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    fileurl = models.TextField(db_column="fileUrl")  # Field name made lowercase.
    filename = models.TextField(db_column="fileName")  # Field name made lowercase.
    filetype = models.TextField(db_column="fileType")  # Field name made lowercase.
    filesize = models.IntegerField(db_column="fileSize")  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "groupMessageFile"


class Groupmember(models.Model):
    memberid = models.TextField(
        db_column="memberId", primary_key=True
    )  # Field name made lowercase.
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    groupid = models.ForeignKey(
        Group, models.DO_NOTHING, db_column="groupId"
    )  # Field name made lowercase.
    jobid = models.ForeignKey(
        Job, models.DO_NOTHING, db_column="jobId"
    )  # Field name made lowercase.
    role = models.TextField()

    class Meta:
        managed = False
        db_table = "groupmember"


class Interests(models.Model):
    intestid = models.TextField(
        db_column="Intestid", primary_key=True
    )  # Field name made lowercase.
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    name = models.TextField()
    description = models.TextField(
        db_column="Description"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "interests"


class Jobrequirements(models.Model):
    requirementsid = models.TextField(
        db_column="requirementsId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField()
    jobid = models.ForeignKey(
        Job, models.DO_NOTHING, db_column="jobId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "jobrequirements"


class Message(models.Model):
    msgid = models.TextField(
        db_column="msgId", primary_key=True
    )  # Field name made lowercase.
    content = models.TextField()
    date = models.DateTimeField()
    matchid = models.ForeignKey(
        Application, models.DO_NOTHING, db_column="matchId"
    )  # Field name made lowercase.
    senderid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="senderId"
    )  # Field name made lowercase.
    isedited = models.BooleanField(db_column="isEdited")  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column="isDeleted")  # Field name made lowercase.
    lasteditedat = models.DateTimeField(
        db_column="lastEditedAt", blank=True, null=True
    )  # Field name made lowercase.
    replytoid = models.ForeignKey(
        "self", models.DO_NOTHING, db_column="replyToId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "message"


class Messagefile(models.Model):
    id = models.TextField(primary_key=True)
    messageid = models.ForeignKey(
        Message, models.DO_NOTHING, db_column="messageId"
    )  # Field name made lowercase.
    userid = models.ForeignKey(
        "User", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    fileurl = models.TextField(db_column="fileUrl")  # Field name made lowercase.
    filename = models.TextField(db_column="fileName")  # Field name made lowercase.
    filetype = models.TextField(db_column="fileType")  # Field name made lowercase.
    filesize = models.IntegerField(db_column="fileSize")  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "messageFile"


class Notifications(models.Model):
    notification = models.TextField(primary_key=True)
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    content = models.TextField()
    posted = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "notifications"


class Skills(models.Model):
    skillid = models.TextField(
        db_column="skillId", primary_key=True
    )  # Field name made lowercase.
    name = models.TextField()
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")

    class Meta:
        managed = False
        db_table = "skills"


class Timings(models.Model):
    timeid = models.TextField(
        db_column="timeId", primary_key=True
    )  # Field name made lowercase.
    starttime = models.DateTimeField(
        db_column="Starttime"
    )  # Field name made lowercase.
    endtime = models.DateTimeField(db_column="Endtime")  # Field name made lowercase.
    id = models.ForeignKey("User", models.DO_NOTHING, db_column="id")
    title = models.TextField(
        db_column="Title", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "timings"


class User(models.Model):
    id = models.TextField(primary_key=True)
    firstname = models.TextField(
        db_column="firstName", blank=True, null=True
    )  # Field name made lowercase.
    lastname = models.TextField(
        db_column="lastName", blank=True, null=True
    )  # Field name made lowercase.
    email = models.TextField(unique=True)
    imageurl = models.TextField(
        db_column="imageUrl", blank=True, null=True
    )  # Field name made lowercase.
    phone = models.TextField(unique=True, blank=True, null=True)
    employee = models.BooleanField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    updatedat = models.DateTimeField(
        db_column="updatedAt"
    )  # Field name made lowercase.
    role = models.TextField()  # This field type is a guess.
    location = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user"


class Userphotos(models.Model):
    photoid = models.TextField(
        db_column="photoId", primary_key=True
    )  # Field name made lowercase.
    id = models.ForeignKey(User, models.DO_NOTHING, db_column="id")
    url = models.TextField()
    position = models.IntegerField()

    class Meta:
        managed = False
        db_table = "userphotos"
