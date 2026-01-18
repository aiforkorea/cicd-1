# apps/auth/forms.py 
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField  #구성요소
from wtforms.validators import DataRequired, Email, length, EqualTo, ValidationError #유효성
from apps.dbmodels import db, User
# form class
class SignUpForm(FlaskForm):      # FlaskForm 상속
    username=StringField("사용자명", 
        validators=[ 
            DataRequired(message="사용자이름 필수"),
            length(max=30,message="30문자이내 입력"),
        ], 
    )
    email=StringField("이메일주소",     
        validators=[ 
            DataRequired(message="메일 주소 필수"),
            Email(message="메일주소 형식 준수"),
        ], 
    )
    password=PasswordField("비밀번호", 
        validators=[ DataRequired(message="비밀번호 필수"),  
            length(min=1,message="10문자 이상 입력"),
        ]
    )
    confirm_password=PasswordField("비밀번호확인", 
        validators=[DataRequired(), EqualTo('password')
        ])
    submit=SubmitField("회원가입")
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 사용 중인 사용자 이름입니다.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 사용 중인 이메일 주소입니다.')    
# form class 추가 - SignUpForm 클래스와 유사
class LoginForm(FlaskForm):      # FlaskForm 상속
    email=StringField("이메일주소", 
        validators=[ DataRequired(message="메일 주소 필수"),
        Email(message="메일주소 형식 준수"), #email_validator 설치필수
    ], )
    password=PasswordField("비밀번호", 
        validators=[ DataRequired(message="비밀번호 필수")]  )
    remember = BooleanField('로그인 정보 기억')
    submit=SubmitField("로그인")

# form class 추가 - 비밀번호 변경 폼
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    new_password = PasswordField('새 비밀번호', validators=[DataRequired(), length(min=1)])
    confirm_new_password = PasswordField('새 비밀번호 확인', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('비밀번호 변경')
        
# 1단계: 재설정 링크를 받기 위해 이메일을 입력하는 폼
class ResetPasswordRequestForm(FlaskForm):
    email = StringField("가입된 이메일 주소", 
        validators=[DataRequired(), Email(message="올바른 이메일 형식이 아닙니다.")])
    submit = SubmitField("재설정 링크 받기")

# 2단계: 메일 링크 클릭 후 새 비밀번호를 입력하는 폼
class ResetPasswordForm(FlaskForm):
    password = PasswordField("새 비밀번호", 
        validators=[DataRequired(), length(min=10, message="10자 이상 입력하세요.")])
    confirm_password = PasswordField("비밀번호 확인", 
        validators=[DataRequired(), EqualTo('password', message="비밀번호가 일치하지 않습니다.")])
    submit = SubmitField("비밀번호 변경 완료")
