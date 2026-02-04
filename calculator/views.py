from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib import messages
from django.core.files.base import ContentFile

from .models import Execution
from .services import process_cashflow


def index(request):
    """Main page - upload form and execution history."""
    executions = Execution.objects.all()[:20]
    return render(request, 'calculator/index.html', {'executions': executions})


def upload(request):
    """Handle CSV file upload."""
    if request.method != 'POST':
        return redirect('calculator:index')

    if 'input_file' not in request.FILES:
        messages.error(request, 'No file selected. Please upload a CSV file.')
        return redirect('calculator:index')

    input_file = request.FILES['input_file']

    if not input_file.name.endswith('.csv'):
        messages.error(request, 'Invalid file type. Please upload a CSV file.')
        return redirect('calculator:index')

    # Create execution record with pending status
    execution = Execution.objects.create(
        input_file=input_file,
        status='pending',
    )

    messages.success(request, f'File "{input_file.name}" uploaded successfully. Click "Process" to run calculations.')
    return redirect('calculator:detail', execution_id=execution.id)


def detail(request, execution_id):
    """View execution details."""
    execution = get_object_or_404(Execution, id=execution_id)
    return render(request, 'calculator/detail.html', {'execution': execution})


def process(request, execution_id):
    """Process the uploaded CSV file and generate output."""
    execution = get_object_or_404(Execution, id=execution_id)

    if execution.status not in ('pending', 'failed'):
        messages.warning(request, 'This execution has already been processed.')
        return redirect('calculator:detail', execution_id=execution.id)

    execution.status = 'processing'
    execution.save()

    try:
        # Open and process the input file
        with execution.input_file.open('rb') as f:
            output_csv, input_rows, output_rows = process_cashflow(f)

        # Save the output file
        output_filename = f'output_{execution.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        execution.output_file.save(output_filename, ContentFile(output_csv.encode('utf-8')))

        # Update execution record
        execution.status = 'completed'
        execution.input_rows = input_rows
        execution.output_rows = output_rows
        execution.completed_at = datetime.now()
        execution.save()

        messages.success(request, f'Processing complete! {input_rows} employees processed, {output_rows} output rows generated.')

    except Exception as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.save()
        messages.error(request, f'Processing failed: {str(e)}')

    return redirect('calculator:detail', execution_id=execution.id)


def download_input(request, execution_id):
    """Download the input CSV file."""
    execution = get_object_or_404(Execution, id=execution_id)
    if not execution.input_file:
        messages.error(request, 'Input file not found.')
        return redirect('calculator:detail', execution_id=execution.id)

    response = FileResponse(execution.input_file.open('rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{execution.input_file.name.split("/")[-1]}"'
    return response


def download_output(request, execution_id):
    """Download the output CSV file."""
    execution = get_object_or_404(Execution, id=execution_id)
    if not execution.output_file:
        messages.error(request, 'Output file not found. Please process the input first.')
        return redirect('calculator:detail', execution_id=execution.id)

    response = FileResponse(execution.output_file.open('rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{execution.output_file.name.split("/")[-1]}"'
    return response


def history(request):
    """View all execution history."""
    executions = Execution.objects.all()
    return render(request, 'calculator/history.html', {'executions': executions})
