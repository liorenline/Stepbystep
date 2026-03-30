from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.main import main_bp
from app.extensions import db
from app.models import Deck, Card, StudyProgress


@main_bp.route("/")
@login_required
def dashboard():
    decks = Deck.query.filter_by(user_id=current_user.id).order_by(Deck.updated_at.desc()).all()
    progress_map = {
        p.deck_id: p
        for p in StudyProgress.query.filter_by(user_id=current_user.id).all()
    }
    return render_template("main/dashboard.html", decks=decks, progress_map=progress_map)




@main_bp.route("/decks/<int:deck_id>")
@login_required
def view_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        abort(403)

    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()
    return render_template("main/deck.html", deck=deck, progress=progress)




@main_bp.route("/decks/<int:deck_id>/delete", methods=["POST"])
@login_required
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        abort(403)

    db.session.delete(deck)
    db.session.commit()
    flash("Deck deleted.", "info")
    return redirect(url_for("main.dashboard"))


@main_bp.route("/decks/<int:deck_id>/cards/<int:card_id>/delete", methods=["POST"])
@login_required
def delete_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        abort(403)

    card = Card.query.get_or_404(card_id)
    if card.deck_id != deck.id:
        abort(404)

    db.session.delete(card)
    db.session.commit()
    flash("Card deleted.", "info")
    return redirect(url_for("main.view_deck", deck_id=deck.id))


@main_bp.route("/decks/<int:deck_id>/study")
@login_required
def study(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        abort(403)

    if not deck.cards:
        flash("This deck has no cards yet.", "warning")
        return redirect(url_for("main.view_deck", deck_id=deck.id))

    return render_template("main/study.html", deck=deck)


@main_bp.route("/decks/<int:deck_id>/progress", methods=["POST"])
@login_required
def save_progress(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        abort(403)

    cards_studied = int(request.form.get("cards_studied", 0))
    cards_correct = int(request.form.get("cards_correct", 0))

    progress = StudyProgress.query.filter_by(user_id=current_user.id, deck_id=deck_id).first()
    if not progress:
        progress = StudyProgress(user_id=current_user.id, deck_id=deck_id)
        db.session.add(progress)

    progress.cards_studied = cards_studied
    progress.cards_correct = cards_correct
    from datetime import datetime
    progress.last_studied_at = datetime.utcnow()
    db.session.commit()

    flash("Progress saved!", "success")
    return redirect(url_for("main.view_deck", deck_id=deck.id))
