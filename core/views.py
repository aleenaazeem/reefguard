from django.views.generic import TemplateView
from .models import Reef, Event, Article

class HomeView(TemplateView):
    """Home page view with featured content and recent activity."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_articles'] = Article.objects.filter(
            published=True, featured=True
        )[:3]
        context['recent_events'] = Event.objects.select_related('reef')[:5]
        context['reef_count'] = Reef.objects.count()
        context['event_count'] = Event.objects.count()
        return context

class EventListView(ListView):
    """
    List view for all events with filtering and sorting.
    """
    model = Event
    template_name = 'core/event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('reef', 'reported_by')

        # Filter by event type
        event_type = self.request.GET.get('event_type', '')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filter by severity
        severity = self.request.GET.get('severity', '')
        if severity:
            queryset = queryset.filter(severity=severity)

        # Filter by year
        year = self.request.GET.get('year', '')
        if year:
            queryset = queryset.filter(event_date__year=year)

        # Filter by resolved status
        resolved = self.request.GET.get('resolved', '')
        if resolved in ['true', 'false']:
            queryset = queryset.filter(resolved=(resolved == 'true'))

        # Sorting
        sort = self.request.GET.get('sort', '-event_date')
        if sort in ['event_date', '-event_date', 'severity', '-severity', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPE_CHOICES
        context['severities'] = Event.SEVERITY_CHOICES

        # Get dynamic list of years from events
        years = Event.objects.dates('event_date', 'year', order='DESC')
        context['years'] = [date.year for date in years]

        context['current_filters'] = self.request.GET
        context['current_sort'] = self.request.GET.get('sort', '-event_date')
        return context

class CustomPasswordResetView(PasswordResetView):
    """
    Password reset request view.
    """
    template_name = 'core/password_reset.html'
    email_template_name = 'core/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
 
    def form_valid(self, form):
        messages.info(
            self.request,
            'Password reset email has been sent if the email exists in our system.'
        )
        return super().form_valid(form)

class BookmarkListView(LoginRequiredMixin, ListView):
    """
    View to display user's bookmarked reefs.
    """
    model = ReefBookmark
    template_name = 'core/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 12
 
    def get_queryset(self):
        """Get bookmarks for current user."""
        return ReefBookmark.objects.filter(
            user=self.request.user
        ).select_related('reef')
 
 
def bookmark_toggle(request, reef_id):
    """
    Toggle bookmark status for a reef (AJAX endpoint).
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
 
    reef = get_object_or_404(Reef, pk=reef_id)
 
    bookmark, created = ReefBookmark.objects.get_or_create(
        user=request.user,
        reef=reef
    )
 
    if not created:
        # Bookmark exists, so remove it
        bookmark.delete()
        bookmarked = False
        message = f'Removed {reef.name} from bookmarks'
    else:
        bookmarked = True
        message = f'Added {reef.name} to bookmarks'
 
    messages.success(request, message)
 
    return JsonResponse({
        'bookmarked': bookmarked,
        'message': message
    })