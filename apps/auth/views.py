# apps/auth/views.py
from datetime import datetime
from flask import current_app, render_template, flash, url_for, redirect, request
from flask_login import login_user, logout_user
from apps.auth.utils import confirm_token, generate_token, send_email, oauth
from apps.extensions import db
from apps.dbmodels import User
from .forms import SignUpForm, LoginForm
from . import auth  # 현재 패키지(__init__.py)의 auth Blueprint 객체 임포트
# index 엔드포인트
@auth.route("/")
def index():
    return render_template("auth/index.html")
# signup 엔드포인트
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            confirmed=False # 기본값 미인증
        )
        db.session.add(user)
        db.session.commit()
        # 토큰 생성 및 메일 발송
        token = generate_token(user.email, salt='email-confirm-salt')
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        send_email(
            subject="[서비스] 이메일 주소를 인증해주세요",
            to=user.email,
            template="auth/email/confirm", # templates/auth/email/confirm.html 필요
            username=user.username,
            confirm_url=confirm_url
        )
        flash("가입 확인 메일이 발송되었습니다. 이메일을 확인해주세요.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", form=form)
# login 엔드포인트
@auth.route("/login",methods=["GET", "POST"])     
def login():
    current_app.logger.info("메인 페이지에 접근했습니다.")
    current_app.logger.debug("사용자 IP: %s", request.remote_addr)
    form = LoginForm()    # LoginForm 회원로그인 객체 form 생성
    if form.validate_on_submit():
        # 사용자가 입력한 이메일 값을 DEBUG 레벨로 로깅
        current_app.logger.debug("사용자가 입력한 이메일: %s", form.email.data)
        user = User.query.filter_by(email=form.email.data).first()
        # DB에 사용자 존재 및 비번 일치하면
        if user is not None and user.verify_password(form.password.data): 
            if not user.confirmed:
                flash("이메일 인증이 필요합니다. 메일 확인 필요", "warning")
                return redirect(url_for("auth.login"))
            # 사용자 정보 세션 저장
            login_user(user, remember=form.remember.data)
            
            send_email("[보안] 로그인 알림", user.email, "auth/email/login_notification",
                       username=user.username, login_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       ip_address=request.remote_addr, user_agent=request.user_agent.string)

            return redirect(url_for("main.index"))   # main.index로 이동
        # 로그인 실패 메시지
        flash("이메일 주소 및 비번 확인 필요")
    return render_template("auth/login.html",form=form)
# logout 엔드포인트 
@auth.route("/logout")     
def logout():
    # 사용자 로그아웃
    logout_user()
    return redirect(url_for("auth.login"))
@auth.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token, salt='email-confirm-salt')
    if not email:
        flash('인증 링크가 만료되었거나 잘못되었습니다.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('이미 인증된 계정입니다.', 'success')
    else:
        user.confirmed = True
        user.confirmed_at = datetime.now()
        db.session.commit()
        flash('이메일 인증이 완료되었습니다!', 'success')
    return redirect(url_for('main.index'))
@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_token(user.email, salt='password-reset-salt')
            # 여기서 실제로 이메일 발송 함수 호출 (예: send_email(user.email, token))
            flash('비밀번호 재설정 이메일을 발송했습니다.', 'info')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html')
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token, salt='password-reset-salt')
    if not email:
        flash('유효하지 않거나 만료된 토큰입니다.', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        user = User.query.filter_by(email=email).first_or_404()
        user.password = request.form.get('password') # Setter에 의해 해싱됨
        db.session.commit()
        flash('비밀번호가 변경되었습니다.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')

@auth.route('/login/google')
def google_login():
    # 구글 로그인 페이지로 보내버리기
    redirect_uri = url_for('auth.google_authorize', _external=True)
    print(f"DEBUG: 생성된 리디렉션 주소는 -> {redirect_uri}") # 터미널 확인용
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/login/google/callback')
def google_authorize():
    # 구글이 보낸 증명서를 확인하기
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    # DB에서 이 이메일의 사용자가 있는지 확인
    user = User.query.filter_by(email=user_info['email']).first()
    
    if not user:
        # 처음 온 사람이라면 회원가입 시켜주기
        user = User(username=user_info['name'], email=user_info['email'], confirmed=True,
                confirmed_at=datetime.now() # 인증 시간 기록
                # password_hash는 None으로 들어감 (nullable=True이므로 허용됨)  
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    flash(f"{user.username}님, 구글 계정으로 로그인되었습니다!", "success")
    return redirect(url_for('main.index'))
