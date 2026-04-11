from datetime import datetime
from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.api import api_bp
from app.extensions import db, csrf
from app.models import User, EmailCode, Deck, Card, StudyProgress
from app.utils import send_verification_code, validate_password_strength


def api_error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def api_ok(data=None, message=None):
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), 200


@api_bp.route("/register", methods=["POST"])
@csrf.exempt
def api_register():
    data = request.get_json()
    if not data:
        return api_error("JSON body required.")

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not username or not email or not password or not confirm_password:
        return api_error("Missing required fields.")

    if password != confirm_password:
        return api_error("Passwords do not match.")

    errors = validate_password_strength(password)
    if errors:
        return api_error(" ".join(errors) if isinstance(errors, list) else errors)

    existing = User.query.filter_by(email=email).first()
    if existing:
        if not existing.is_verified:
            return api_error("Email registered but not verified. Use resend-verification to get a new code.", 409)
        return api_error("Email already registered.")

    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        code = EmailCode.create_for_user(user, purpose="register")
        send_verification_code(user, code.code, purpose="register")

        return api_ok({"user_id": user.id}, "User created. Verification code sent.")

    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@api_bp.route("/verify-email", methods=["POST"])
@csrf.exempt
def api_verify_email():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    user_id = body.get("user_id")
    code_input = body.get("code", "").strip()

    if not user_id or not code_input:
        return api_error("user_id and code are required.")

    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if user.is_verified:
        return api_ok(message="Email is already verified.")

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="register", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired code.")

    code_record.is_used = True
    user.is_verified = True
    db.session.commit()

    return api_ok(message="Email verified successfully.")


@api_bp.route("/resend-verification", methods=["POST"])
@csrf.exempt
def api_resend_verification():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    email = body.get("email", "").strip().lower()
    if not email:
        return api_error("Email is required.")

    user = User.query.filter_by(email=email).first()
    if not user:
        return api_error("No account found with this email.", 404)

    if user.is_verified:
        return api_ok(message="Email is already verified. You can log in.")

    try:
        code = EmailCode.create_for_user(user, purpose="register")
        send_verification_code(user, code.code, purpose="register")
        return api_ok({"user_id": user.id}, "Verification code resent.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@api_bp.route("/login", methods=["POST"])
@csrf.exempt
def api_login():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return api_error("Email and password are required.")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return api_error("Invalid credentials.", 401)

    if not user.is_verified:
        return api_error("Please verify your email first.", 403)

    if user.two_fa_enabled:
        code = EmailCode.create_for_user(user, purpose="2fa")
        send_verification_code(user, code.code, purpose="2fa")
        return api_ok({"requires_2fa": True, "user_id": user.id}, "2FA code sent to email.")

    login_user(user)
    return api_ok(
        {"user_id": user.id, "username": user.username, "email": user.email},
        "Logged in successfully."
    )


@api_bp.route("/verify-2fa", methods=["POST"])
@csrf.exempt
def api_verify_2fa():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    user_id = body.get("user_id")
    code_input = body.get("code", "").strip()

    if not user_id or not code_input:
        return api_error("user_id and code are required.")

    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if not user.two_fa_enabled:
        return api_error("2FA is not enabled for this account.")

    if not user.is_verified:
        return api_error("Account is not verified.", 403)

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="2fa", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired 2FA code.")

    code_record.is_used = True
    db.session.commit()
    login_user(user)

    return api_ok(
        {"user_id": user.id, "username": user.username, "email": user.email},
        "Logged in successfully."
    )


@api_bp.route("/logout", methods=["POST"])
@login_required
@csrf.exempt
def api_logout():
    logout_user()
    return api_ok(message="Logged out successfully.")


@api_bp.route("/decks", methods=["GET"])
@login_required
def api_get_decks():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.updated_at.desc()).all()
    progress_map = {
        p.deck_id: p
        for p in StudyProgress.query.filter_by(user_id=current_user.id).all()
    }

    result = []
    for deck in decks:
        p = progress_map.get(deck.id)
        result.append({
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
            "card_count": deck.card_count(),
            "cards_studied": p.cards_studied if p else 0,
            "completion_percent": p.completion_percent() if p else 0,
            "updated_at": deck.updated_at.isoformat(),
        })

    return api_ok(result)


@api_bp.route("/decks", methods=["POST"])
@login_required
@csrf.exempt
def api_create_deck():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    title = body.get("title", "").strip()
    if not title:
        return api_error("Title is required.")
    if len(title) > 120:
        return api_error("Title must be 120 characters or fewer.")

    description = body.get("description", "").strip()

    deck = Deck(user_id=current_user.id, title=title, description=description)
    db.session.add(deck)
    db.session.commit()

    return api_ok({"id": deck.id, "title": deck.title}, "Deck created.")


@api_bp.route("/decks/<int:deck_id>", methods=["GET"])
@login_required
def api_get_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    p = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()
    return api_ok({
        "id": deck.id,
        "title": deck.title,
        "description": deck.description,
        "card_count": deck.card_count(),
        "cards_studied": p.cards_studied if p else 0,
        "completion_percent": p.completion_percent() if p else 0,
        "updated_at": deck.updated_at.isoformat(),
    })


@api_bp.route("/decks/<int:deck_id>", methods=["PUT"])
@login_required
@csrf.exempt
def api_update_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    title = body.get("title", deck.title).strip()
    if not title:
        return api_error("Title cannot be empty.")
    if len(title) > 120:
        return api_error("Title must be 120 characters or fewer.")

    deck.title = title
    deck.description = body.get("description", deck.description)
    deck.updated_at = datetime.utcnow()
    db.session.commit()

    return api_ok({"id": deck.id, "title": deck.title}, "Deck updated.")


@api_bp.route("/decks/<int:deck_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    db.session.delete(deck)
    db.session.commit()
    return api_ok(message="Deck deleted.")


@api_bp.route("/decks/<int:deck_id>/cards", methods=["GET"])
@login_required
def api_get_cards(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    cards = [
        {"id": c.id, "question": c.question, "answer": c.answer}
        for c in deck.cards
    ]
    return api_ok(cards)


@api_bp.route("/decks/<int:deck_id>/cards", methods=["POST"])
@login_required
@csrf.exempt
def api_create_card(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    question = body.get("question", "").strip()
    answer = body.get("answer", "").strip()

    if not question or not answer:
        return api_error("Question and answer are required.")

    card = Card(deck_id=deck.id, question=question, answer=answer)
    db.session.add(card)
    deck.updated_at = datetime.utcnow()
    db.session.commit()

    return api_ok({"id": card.id, "question": card.question, "answer": card.answer}, "Card added.")


@api_bp.route("/decks/<int:deck_id>/cards/<int:card_id>", methods=["GET"])
@login_required
def api_get_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        return api_error("Card not found in this deck.", 404)

    return api_ok({"id": card.id, "question": card.question, "answer": card.answer})


@api_bp.route("/decks/<int:deck_id>/cards/<int:card_id>", methods=["PUT"])
@login_required
@csrf.exempt
def api_update_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        return api_error("Card not found in this deck.", 404)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    question = body.get("question", card.question).strip()
    answer = body.get("answer", card.answer).strip()

    if not question or not answer:
        return api_error("Question and answer cannot be empty.")

    card.question = question
    card.answer = answer
    deck.updated_at = datetime.utcnow()
    db.session.commit()

    return api_ok({"id": card.id, "question": card.question, "answer": card.answer}, "Card updated.")


@api_bp.route("/decks/<int:deck_id>/cards/<int:card_id>", methods=["DELETE"])
@login_required
@csrf.exempt
def api_delete_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        return api_error("Card not found in this deck.", 404)

    db.session.delete(card)
    deck.updated_at = datetime.utcnow()
    db.session.commit()
    return api_ok(message="Card deleted.")


@api_bp.route("/offline/<int:deck_id>", methods=["GET"])
@login_required
def api_offline_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return api_error("Forbidden.", 403)

    cards = [{"id": c.id, "question": c.question, "answer": c.answer} for c in deck.cards]
    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()

    return api_ok({
        "deck": {
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
        },
        "cards": cards,
        "progress": {
            "cards_studied": progress.cards_studied if progress else 0,
            "cards_correct": progress.cards_correct if progress else 0,
            "completion_percent": progress.completion_percent() if progress else 0,
        },
    })


@api_bp.route("/sync-progress", methods=["POST"])
@login_required
@csrf.exempt
def api_sync_progress():
    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    deck_id = body.get("deck_id")
    if deck_id is None:
        return api_error("deck_id is required.")

    try:
        cards_studied = int(body.get("cards_studied", 0))
        cards_correct = int(body.get("cards_correct", 0))
    except (TypeError, ValueError):
        return api_error("cards_studied and cards_correct must be integers.")

    if cards_studied < 0 or cards_correct < 0:
        return api_error("cards_studied and cards_correct must be non-negative.")

    if cards_correct > cards_studied:
        return api_error("cards_correct cannot exceed cards_studied.")

    deck = Deck.query.get(deck_id)
    if not deck or deck.user_id != current_user.id:
        return api_error("Deck not found.", 404)

    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()
    if not progress:
        progress = StudyProgress(user_id=current_user.id, deck_id=deck_id)
        db.session.add(progress)

    progress.cards_studied = cards_studied
    progress.cards_correct = cards_correct
    progress.last_studied_at = datetime.utcnow()
    db.session.commit()

    return api_ok({
        "deck_id": deck_id,
        "cards_studied": progress.cards_studied,
        "cards_correct": progress.cards_correct,
        "completion_percent": progress.completion_percent(),
    }, "Progress synced.")


@api_bp.route("/user/<int:user_id>", methods=["GET"])
@csrf.exempt
def api_get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)
    return api_ok({
        "username": user.username,
        "email": user.email,
        "two_factor_enabled": user.two_fa_enabled,
    })


@api_bp.route("/user/<int:user_id>", methods=["PUT"])
@csrf.exempt
def api_update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    username = body.get("username", "").strip()
    email = body.get("email", "").strip().lower()

    if username:
        user.username = username
    if email:
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            return api_error("Email already in use.")
        user.email = email

    db.session.commit()
    return api_ok({"username": user.username, "email": user.email}, "Profile updated.")


# ─────────────────────────────────────────────
#  Password change with email verification
# ─────────────────────────────────────────────

@api_bp.route("/user/<int:user_id>/send-change-password-code", methods=["POST"])
@csrf.exempt
def api_send_change_password_code(user_id):
    """Send a 6-digit code to the user's email to confirm a password change."""
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    try:
        code = EmailCode.create_for_user(user, purpose="change_password")
        send_verification_code(user, code.code, purpose="change_password")
        return api_ok(message="Verification code sent to your email.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@api_bp.route("/user/<int:user_id>/change-password", methods=["POST"])
@csrf.exempt
def api_change_password(user_id):
    """Verify the code and apply the new password."""
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    code_input = body.get("code", "").strip()
    new_password = body.get("password", "").strip()

    if not code_input:
        return api_error("code is required.")
    if not new_password:
        return api_error("password is required.")

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="change_password", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired code.")

    errors = validate_password_strength(new_password)
    if errors:
        return api_error(" ".join(errors) if isinstance(errors, list) else errors)

    code_record.is_used = True
    user.set_password(new_password)
    db.session.commit()

    return api_ok(message="Password changed successfully.")


# ─────────────────────────────────────────────
#  2FA setup (enable)
# ─────────────────────────────────────────────

@api_bp.route("/user/<int:user_id>/2fa/send-code", methods=["POST"])
@csrf.exempt
def api_2fa_send_code(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if user.two_fa_enabled:
        return api_error("2FA is already enabled.")

    try:
        code = EmailCode.create_for_user(user, purpose="2fa_setup")
        send_verification_code(user, code.code, purpose="2fa_setup")
        return api_ok(message="Verification code sent to your email.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@api_bp.route("/user/<int:user_id>/2fa/enable", methods=["POST"])
@csrf.exempt
def api_2fa_enable(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if user.two_fa_enabled:
        return api_error("2FA is already enabled.")

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    code_input = body.get("code", "").strip()
    if not code_input:
        return api_error("code is required.")

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="2fa_setup", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired code.")

    code_record.is_used = True
    user.two_fa_enabled = True
    db.session.commit()

    return api_ok(message="Two-factor authentication enabled successfully.")


# ─────────────────────────────────────────────
#  2FA disable with email verification
# ─────────────────────────────────────────────

@api_bp.route("/user/<int:user_id>/2fa/send-disable-code", methods=["POST"])
@csrf.exempt
def api_2fa_send_disable_code(user_id):
    """Send a 6-digit code to confirm disabling 2FA."""
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if not user.two_fa_enabled:
        return api_error("2FA is not enabled.")

    try:
        code = EmailCode.create_for_user(user, purpose="2fa_disable")
        send_verification_code(user, code.code, purpose="2fa_disable")
        return api_ok(message="Verification code sent to your email.")
    except Exception as e:
        db.session.rollback()
        return api_error(str(e), 500)


@api_bp.route("/user/<int:user_id>/2fa/disable", methods=["POST"])
@csrf.exempt
def api_2fa_disable(user_id):
    """Verify the code and disable 2FA."""
    user = User.query.get(user_id)
    if not user:
        return api_error("User not found.", 404)

    if not user.two_fa_enabled:
        return api_error("2FA is not enabled.")

    body = request.get_json()
    if not body:
        return api_error("JSON body required.")

    code_input = body.get("code", "").strip()
    if not code_input:
        return api_error("code is required.")

    code_record = EmailCode.query.filter_by(
        user_id=user.id, purpose="2fa_disable", is_used=False
    ).order_by(EmailCode.created_at.desc()).first()

    if not code_record or not code_record.is_valid() or code_record.code != code_input:
        return api_error("Invalid or expired code.")

    code_record.is_used = True
    user.two_fa_enabled = False
    db.session.commit()

    return api_ok(message="Two-factor authentication disabled.")