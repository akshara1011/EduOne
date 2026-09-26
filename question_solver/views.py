"""
Question Scanner views — upload image, OCR, get AI solution.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
import json

from .models import ScannedQuestion
from chatbot.gemini_service import solve_question_with_image


@login_required
def scanner_home(request):
    """Question scanner page."""
    recent_scans = ScannedQuestion.objects.filter(student=request.user)[:5]
    return render(request, 'question_solver/scanner.html', {
        'recent_scans': recent_scans
    })


@login_required
@require_POST
def upload_question(request):
    """Upload image, send to Gemini Vision, return solution."""
    image_file = request.FILES.get('image')

    if not image_file:
        return JsonResponse({'error': 'No image provided'}, status=400)

    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. Use JPG/PNG/WebP.'}, status=400)

    # Validate file size (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'Image too large. Max 5MB.'}, status=400)

    # Read image bytes
    image_bytes = image_file.read()

    # Send to Gemini Vision
    result = solve_question_with_image(image_bytes, image_file.content_type)
    solution_text = result.get('solution') or result.get('full_response') or ''

    # Save the scan record
    scan = ScannedQuestion.objects.create(
        student=request.user,
        ai_solution=solution_text,
        error=result.get('error') or ''
    )
    scan.image.save(image_file.name, ContentFile(image_bytes))

    # Record learning activity for streak
    from progress.services import record_learning_activity
    record_learning_activity(
        student=request.user,
        activity_type='scan_question',
        description='Scanned a question'
    )

    return JsonResponse({
        'scan_id': scan.id,
        'solution': solution_text,
        'error': result.get('error')
    })



@login_required
def scan_result(request, scan_id):
    """View a specific scan result."""
    scan = get_object_or_404(ScannedQuestion, id=scan_id, student=request.user)
    return render(request, 'question_solver/result.html', {'scan': scan})
