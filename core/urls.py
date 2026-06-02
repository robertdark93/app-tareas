from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms_auth import LockoutAuthenticationForm

urlpatterns = [
    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        authentication_form=LockoutAuthenticationForm,
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Home
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),

    # Tasks
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('tasks/bulk-action/', views.bulk_action, name='bulk_action'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),

    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<int:pk>/delete/', views.tag_delete, name='tag_delete'),

    # Attachments
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),

    # Notes
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('notes/<int:pk>/update/', views.NoteUpdateView.as_view(), name='note_update'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    # Kanban
    path('kanban/', views.kanban, name='kanban'),
    path('kanban/<int:pk>/update/', views.kanban_update, name='kanban_update'),

    # Summary & Exports
    path('summary/', views.summary, name='summary'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/xlsx/', views.export_xlsx, name='export_xlsx'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.notification_read, name='notification_read'),
    path('notifications/read-all/', views.notification_read_all, name='notification_read_all'),
    path('notifications/unread-count/', views.notification_unread_count, name='notification_unread_count'),

    # Admin Panel
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin-panel/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/tasks/', views.admin_tasks, name='admin_tasks'),
    path('admin-panel/board/', views.admin_board, name='admin_board'),
    path('admin-panel/departments/', views.admin_departments, name='admin_departments'),
    path('admin-panel/departments/create/', views.admin_department_create, name='admin_department_create'),
    path('admin-panel/departments/<int:pk>/edit/', views.admin_department_edit, name='admin_department_edit'),
    path('admin-panel/backups/', views.admin_backups, name='admin_backups'),

    # SubTask reorder
    path('tasks/<int:pk>/reorder-subtasks/', views.subtask_reorder, name='subtask_reorder'),

    # Share
    path('tasks/<int:pk>/generate-share-token/', views.generate_share_token, name='generate_share_token'),
    path('shared/<uuid:token>/', views.shared_task, name='shared_task'),

    # Watch / Unwatch
    path('tasks/<int:pk>/watch/', views.watch_task, name='watch_task'),
    path('tasks/<int:pk>/unwatch/', views.unwatch_task, name='unwatch_task'),

    # Task Lock
    path('tasks/<int:pk>/lock/', views.task_lock, name='task_lock'),
    path('tasks/<int:pk>/unlock/', views.task_unlock, name='task_unlock'),
]
