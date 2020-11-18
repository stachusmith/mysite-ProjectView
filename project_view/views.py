from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import naturaltime


from django.views.generic import TemplateView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
#from project_view.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from project_view.models import Part, Client, Project, Module, Supplier, Topic, Fixing, Fix
from project_view.forms import CreateForm #, CommentForm

#from project_view.utils import dump_queries

#from django.db.models import Q

class PartListView(View):
    model = Part
    # By convention:
    template_name = "project_view/part_list.html"
    def get(self, request) :
        part_list = Part.objects.all() #pulling objects from db

        ctx = {'part_list' : part_list} # leaving out for now: 'favorites': favorites, 'search': strval}
        return render(request, self.template_name, ctx)

class PartDetailView(DetailView, LoginRequiredMixin):
    model = Part
    template_name = "project_view/part_detail.html"
    def get(self, request, pk) :
        x = Part.objects.get(id=pk)
        context = { 'part' : x }
        return render(request, self.template_name, context)

class PartCreateView(LoginRequiredMixin, View):
    success_url=reverse_lazy('project_view:main')
    template_name='project_view/part_form.html'

    def get(self, request):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)
        #form is produced from forms.py

    def post(self, request):
        form = CreateForm(request.POST)
        #because of the picture fuctionality

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        #if form isn't valid, refresh the form            

    # Add owner to the model before saving
        part = form.save(commit=False)
        part.owner = self.request.user #pull user from request and make him pic owner
        part.save()
        return redirect(self.success_url)


class PartUpdateView(LoginRequiredMixin, View):
    success_url=reverse_lazy('project_view:main')
    template_name='project_view/part_form.html'

    def get(self, request, pk):
        part = get_object_or_404(Part, id=pk, owner=self.request.user) #from db
        form = CreateForm(instance=part)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk):
        part = get_object_or_404(Part, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, instance=part)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        part = form.save #(commit=False)
        #part.save()

        return redirect(self.success_url)


class PartDeleteView(DeleteView, LoginRequiredMixin):
    model = Part

    def get_queryset(self):
        print('delete get_queryset called')
        qs = super(DeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)

# Clients
#-------------------------------------------------------------------------------

class ClientListView(ListView):
    model = Client

class ClientDetailView(View, LoginRequiredMixin):
    model = Client
    
    # By convention:
    template_name = "project_view/client_detail.html"
    def get(self, request, pk) :
        x = Client.objects.get(id=pk) #pulling the client from db
        project_list = Project.objects.filter(name=x) #pulling projects belonging to client from db

        ctx = {'client' : x, 'project_list' : project_list}
        return render(request, self.template_name, ctx)

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['name']
    success_url=reverse_lazy('project_view:clients')

    def form_valid(self, form):
        print('form_valid called')
        object = form.save(commit=False)
        object.owner = self.request.user
        object.save()
        return super(ClientCreateView, self).form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    
    model = Client
    fields = ['name']
    success_url=reverse_lazy('project_view:clients')
    def get_queryset(self):
        print('update get_queryset called')
        """ Limit a User to only modifying their own data. """
        qs = super(ClientUpdateView, self).get_queryset()
        return qs.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url=reverse_lazy('project_view:clients')
    def get_queryset(self):
        print('delete get_queryset called')
        qs = super(DeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)

# Clients
#-------------------------------------------------------------------------------

class ProjectListView(ListView):
    model = Project