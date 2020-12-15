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
from project_view.forms import CreateProjectForm, CreateModuleForm, CreatePartForm, CreateFixingForm, CreateFixForm, CreateTopicForm, UpdateTopicForm, CreateEntryForm

#from project_view.utils import dump_queries

#from django.db.models import Q

class TopicDetailView(View, LoginRequiredMixin):
    model = Topic
    template_name = 'project_view/topic_detail.html'
    def get(self, request, pk_part, pk_topi) :
        topic = self.model.objects.get(id=pk_topi)
        print(topic)
        part = Part.objects.get(id=pk_part)
        print(part)
        module_number = part.module_id
        module = Module.objects.get(id=module_number)
        picture_list = Picture.objects.filter(topic_id=pk_topi)
        entries_list = Entry.objects.filter(topic_id=pk_topi)
        
        context = { 'part' : part, 'module': module, 'topic': topic, 'picture_list':picture_list, 'entries_list': entries_list }
        return render(request, self.template_name, context)

class TopicCreateView(View, LoginRequiredMixin):

    template_name='project_view/topic_form.html'
    
    def get(self, request, pk_part):
        part = Part.objects.get(id=pk_part)
        print(part)
        
        form_data = { 'part':part }
        form = CreateTopicForm(initial=form_data)

        #get module
        module_number = part.module_id
        module = Module.objects.get(id=module_number)
        
        
        #limit options in dropdown:
        form.fields['part'].queryset = Part.objects.filter(id=pk_part)
        ctx= { 'form':form, 'module':module, 'part':part }
        return render(request, self.template_name, ctx)
        
    def post(self, request, pk_part):
        form = CreateTopicForm(request.POST, request.FILES or None)
        pk_topic=request.POST['title']
        print(pk_topic)
        #part = Part.objects.get(id=pk_part)
        if not form.is_valid():
            ctx = {'form': form }
            return render(request, self.template_name, ctx)
        topic = form.save(commit=False)
        topic.owner = self.request.user
        topic.save()
        pk_topi=topic.id
        return redirect(reverse('project_view:topic_update', args=[pk_part, pk_topi]))

class TopicUpdateView(UpdateView, LoginRequiredMixin):
    template_name='project_view/update_topic_form.html'
    
    def get(self, request, pk_part, pk_topi):
        part = Part.objects.get(id=pk_part)
        topic = Topic.objects.get(id=pk_topi)
        #get module
        module_number = part.module_id
        module = Module.objects.get(id=module_number)
        picture_list = Picture.objects.filter(topic_id=pk_topi)
        form = UpdateTopicForm()
        entry_form = CreateEntryForm()
        entries_list = Entry.objects.filter(topic_id=pk_topi)
        
        
        ctx= { 'form':form, 'topic':topic, 'module':module, 'part':part, 'picture_list': picture_list, 'entry_form':entry_form, 'entries_list': entries_list }
        return render(request, self.template_name, ctx)
        
    def post(self, request, pk_part, pk_topi):
        form = UpdateTopicForm(request.POST)
        print(request.POST)
        picture_list = Picture.objects.filter(topic_id=pk_topi)
        #part = Part.objects.get(id=pk_part)
        if not form.is_valid():
            ctx = {'form': form }
            return render(request, self.template_name, ctx)
        
        topic = form.save(commit=False)
        topic.owner = self.request.user

        #as not to discard the picture on save (change 'session' for 1 to 0)
        for picture in picture_list:
            picture.session = 0
            print(picture.session)
            picture.save()
        topic.save()

        
        return redirect(reverse('project_view:topic_detail', args=[pk_part, pk_topi]))

class TopicCancelView(LoginRequiredMixin, View):

    template_name='project_view/topic_confirm_cancel.html'
    def get (self, request, pk_topi):
        topic = get_object_or_404(Topic, pk=pk_topi)
        part = topic.part.id
        
        arg = [topic.part.module_id, topic.part_id]
        picture_list = Picture.objects.filter(session=1, owner=self.request.user)
        print(picture_list)
        if not picture_list:
            return redirect(reverse('project_view:part_detail', args=arg))
        ctx = {'picture_list': picture_list, 'topic':topic, 'part':part}
        return render(request, self.template_name, ctx)

    def post(self, request, pk_topi):
        topic = get_object_or_404(Topic, pk=pk_topi)
        arg = [topic.part.module_id, topic.part_id]
        picture_list = Picture.objects.filter(session=1, owner=self.request.user)
        for picture in picture_list:
            picture.delete()
        print(arg)
        return redirect(reverse('project_view:part_detail', args=arg))

class TopicDeleteView(LoginRequiredMixin, View):
    
    template_name='project_view/topic_confirm_delete.html'
    def get (self, request, pk_part, pk_topi):
        topic = get_object_or_404(Topic, pk=pk_topi, owner=self.request.user)
        print(topic)
        ctx = {'topic': topic}
        return render(request, self.template_name, ctx)
    
#    def get_queryset(self):
#        print('delete get_queryset called')
#        qs = super(ModuleDeleteView, self).get_queryset()
#        return qs.filter(owner=self.request.user)

    def post(self, request, pk_part, pk_topi):
        topic = get_object_or_404(Topic, pk=pk_topi)
        arg = [topic.part.module_id, topic.part_id]
        
        topic.delete()
        print(arg)
        return redirect(reverse('project_view:part_detail', args=arg))


#Pictures--------------------------------------------------------------------------------------

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError



@method_decorator(csrf_exempt, name='dispatch')
class AddPictureView(LoginRequiredMixin, View):

    def post(self, request, pk_topi) :
        
        
        pic_file = request.FILES['inpFile']
        print('pic_file:',pic_file)
        
        pic_bytearr=pic_file.read()
        print('pic_bytearr:',pic_bytearr)
        
        Picture.objects.create(picture=pic_bytearr, owner = self.request.user, topic_id=pk_topi, content_type=pic_file.content_type, session=1)
        
        return HttpResponse()

#@method_decorator(csrf_exempt, name='dispatch')
class DeletePictureView(LoginRequiredMixin, View):
    
    template_name='project_view/picture_confirm_delete.html'
    def get (self, request, pk_topi, pk_pict):
        picture = get_object_or_404(Picture, pk=pk_pict, owner=self.request.user)
        topic = Topic.objects.get(id=pk_topi)
        print(topic)

        ctx = {'picture': picture, 'topic':topic }
        return render(request, self.template_name, ctx)
    
    def post(self, request, pk_topi, pk_pict):
        picture = get_object_or_404(Picture, pk=pk_pict)
        arg = [picture.topic.part_id, picture.topic_id]
        
        picture.delete()
        print(arg)
        return redirect(reverse('project_view:topic_detail', args=arg))

#stream picture----------------------------------------------------------------------------
def stream_file(request, pk_topi, pk_pict):
    pic = get_object_or_404(Picture, id=pk_pict)

    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response