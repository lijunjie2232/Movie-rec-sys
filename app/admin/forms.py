# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from app.models import Admin, Tag

tags = Tag.query.all()


class LoginForm(FlaskForm):
    """管理员登录表单"""
    account = StringField(
        label="login_account",
        validators=[
            DataRequired("Pleasse enter account!")
        ],
        description="账号",
        render_kw={
            "class": "fadeIn second",
            "placeholder": "Pleasse enter account!",
            # "required":"required"
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("Pleasse enter password！")
        ],
        description="password",
        render_kw={
            "class": "fadeIn third",
            "id": "password",
            "placeholder": "Pleasse enter password！",
            # "required": "required"
        }
    )

    submit = SubmitField(
        label="Log In",
        render_kw={
            "value": "Log In",
            "class": "fadeIn fourth",

        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")


class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        validators=[
            DataRequired("请输入标签！")
        ],
        description="标签",
        render_kw={
            "class": "from-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",

        }
    )


class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名！")
        ],
        description="标签",
        render_kw={
            "class": "from-control",
            "placeholder": "请输入片名！"
        }
    )
    # url = FileField(
    #     label="文件",
    #     validators=[
    #         DataRequired("请上传文件！")
    #     ],
    #     description="文件",
    # )
    # info = TextAreaField(
    #     label="简介",
    #     validators=[
    #         DataRequired("请输入简介！")
    #     ],
    #     description="简介",
    #     render_kw={
    #         "class": "from-control",
    #         "row": 27
    #     }
    # )
    # logo = FileField(
    #     label="封面",
    #     validators=[
    #         DataRequired("请上传封面！")
    #     ],
    #     description="封面",
    # )
    # star = SelectField(
    #     label="星级",
    #     validators=[
    #         DataRequired("请选择星级别!")
    #     ],
    #     coerce=int,
    #     choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
    #     description="星级",
    #     render_kw={
    #         "class": "from-control",
    #     }
    # )
    # tag_id = SelectField(
    #     label="标签",
    #     validators=[
    #         DataRequired("请选择星标签!")
    #     ],
    #     coerce=int,
    #     choices=[(v.tagId, v.tag) for v in tags],
    #     description="标签",
    #     render_kw={
    #         "class": "from-control",
    #     }
    # )

    lang = StringField(
        label="语言",
        validators=[
            DataRequired("请输入语言！")
        ],
        description="语言",
        render_kw={
            "class": "from-control",
            "placeholder": "请输入语言！"
        }
    )

    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "class": "from-control",
            "placeholder": "请输入片长！"
        }
    )

    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请选择上映时间！")
        ],
        description="上映时间",
        render_kw={
            "class": "from-control",
            "placeholder": "请选择上映时间!",
            "id": "input_release_time"
        }
    )

    submit = SubmitField(
        label="保存",
        render_kw={
            "class": "btn btn-primary",

        }
    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入预告标题! ")
        ],
        description="预告标题",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告标题! "
        }
    )

    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请输入预告封面! ")
        ],
        description="预告封面",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告封面! "
        }
    )

    submit = SubmitField(
        label="添加",
        render_kw={
            "class": "btn btn-primary",

        }
    )
