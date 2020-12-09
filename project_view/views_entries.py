#----------------------------------------------------------
#in this file you will find the topic & picture views
#----------------------------------------------------------

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.uploadedfile import InMemoryUploadedFile


from django.views.generic import TemplateView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
#from project_view.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from project_view.models import Part, Client, Project, Module, Supplier, Topic, Fixing, Fix, Picture, Entry
from project_view.forms import CreateProjectForm, CreateModuleForm, CreatePartForm, CreateFixingForm, CreateFixForm, CreateTopicForm, UpdateTopicForm

#from project_view.utils import dump_queries

#from django.db.models import Q

class EntryListView(ListView, LoginRequiredMixin):
    model = Fixing

class EntryCreateView(CreateView, LoginRequiredMixin):
    
    template_name='project_view/fixing_form.html'
    
    def get(self, request):
                
        form_data = {'name':''}
        form = CreateFixingForm(initial=form_data)
        
        ctx= { 'form':form }
        return render(request, self.template_name, ctx)

    def post(self, request):
        
        #unused:
        #pk=request.POST['client']
        #print(pk)
        
        form = CreateFixingForm(request.POST)
        
        #if not valid render the form again:
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        #add user as owner before saving:
        fixing = form.save(commit=False)
        fixing.owner = self.request.user
        fixing.save()

        return redirect(reverse('project_view:main'))

class EntryUpdateView(UpdateView, LoginRequiredMixin):
    model = Fix

    fields = ['name']
    success_url=reverse_lazy('project_view:fixing_list')
    def get_queryset(self):
        print('update get_queryset called')
        #Limit a User to only modifying their own data
        qs = super(FixingUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)

class EntryDeleteView(DeleteView, LoginRequiredMixin):
    model = Fixing
    success_url=reverse_lazy('project_view:fixing_list')
    def get_queryset(self):
        print('delete get_queryset called')
        qs = super(FixingDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)