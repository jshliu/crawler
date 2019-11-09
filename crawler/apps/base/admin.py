#coding=utf-8

from django.contrib import admin

from context.context import Context
Task = Context().get("Task")


class TaskAdmin(admin.ModelAdmin):
	list_display = ('crawler', 'key', 'update_time', 'status', 'interval', 'create_time')
	list_display_links = ('update_time', 'create_time')
	list_editable = ('crawler', 'key', 'status', 'interval')
	list_filter = ('crawler', 'status', 'category', 'application', 'interval', 'timeout')
	fields = ('key', 'data', 'producer_id', 'category', 'application', 'crawler', \
		'status', 'interval', 'timeout', 'last_run', 'next_run', 'update_time', 'create_time')
	readonly_fields = ('last_run', 'update_time', 'create_time')
	ordering = ('update_time','-key')
	search_fields = ('key',)


admin.site.register(Task, TaskAdmin)