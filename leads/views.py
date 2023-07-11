from typing import Any, Dict
from django.core.mail import send_mail
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse
from .models import Lead, Category
from .forms import LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, CategoryModelForm
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganisorAndLoginRequiredMixin

class SignupView(generic.CreateView):
  template_name = "registration/signup.html"
  form_class = CustomUserCreationForm
  
  def get_success_url(self):
    return reverse("login")

class LandingPage(generic.TemplateView):
  template_name = "landing.html"


class LeadListView(LoginRequiredMixin, generic.ListView):
  template_name = "leads/lead_list.html"
  context_object_name = "leads"
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Lead.objects.filter(
          organisation=user.userprofile, 
          agent__isnull=False
        )
    else:
      queryset = Lead.objects.filter(
          organisation=user.agent.organisation, 
          agent__isnull=False
        )
      queryset = queryset.filter(agent__user=user)
    return queryset
  
  def get_context_data(self, **kwargs):
    user = self.request.user
    context = super(LeadListView, self).get_context_data(**kwargs)
    if user.is_organisor:
      queryset = Lead.objects.filter(
          organisation=user.userprofile, 
          agent__isnull=True,
        )
      context.update({
        "unassigned_leads": queryset
      })
    return context
    


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
  template_name = "leads/lead_detail.html"
  context_object_name = "lead"
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Lead.objects.filter(organisation=user.userprofile)
    else:
      queryset = Lead.objects.filter(organisation=user.agent.organisation)
      queryset = queryset.filter(agent__user=user)
    return queryset


class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
  template_name = "leads/lead_create.html"
  form_class = LeadModelForm
  
  def get_success_url(self):
    return reverse("leads:lead-list")
  
  def form_valid(self, form):
    lead = form.save(commit=False)
    lead.organisation = self.request.user.userprofile
    lead.save()
    send_mail(
      subject="A lead has been created",
      message="Go to the site to see the new leed",
      from_email="test@test.com",
      recipient_list=["test2@test.com",]
    )
    return super(LeadCreateView, self).form_valid(form)

class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
  template_name = "leads/lead_update.html"
  form_class = LeadModelForm
  
  def get_queryset(self):
    user = self.request.user
    return Lead.objects.filter(organisation=user.userprofile)
  
  def get_success_url(self):
    return reverse("leads:lead-list")


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
  template_name = "leads/lead_delete.html"
  queryset = Lead.objects.all()
  
  def get_success_url(self):
    return reverse("leads:lead-list")
  

class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
  template_name = "leads/assign_agent.html"
  form_class = AssignAgentForm
  
  def get_form_kwargs(self, **kwargs):
    kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
    kwargs.update({
      "request": self.request
    })
    return kwargs
  
  def get_success_url(self):
    return reverse("leads:lead-list")
  
  def form_valid(self, form):
    agent = form.cleaned_data["agent"]
    lead = Lead.objects.get(id=self.kwargs["pk"])
    lead.agent = agent
    lead.save()
    return super(AssignAgentView, self).form_valid(form)
  

class CategoryListView(LoginRequiredMixin, generic.ListView):
  template_name = "leads/category_list.html"
  context_object_name = "category_list"
  
  def get_context_data(self, **kwargs):
    context = super(CategoryListView, self).get_context_data(**kwargs)
    user = self.request.user
    if user.is_organisor:
      queryset = Lead.objects.filter(
        organisation = user.userprofile
      )
    else:
      queryset = Lead.objects.filter(
        organisation = user.agent.organisation
      )
    context.update({
      "unassigned_lead_count": queryset.filter(category__isnull=True).count()
    })
    return context
    
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Category.objects.filter(
        organisation = user.userprofile
      )
    else:
      queryset = Category.objects.filter(
        organisation = user.agent.organisation
      )
    return queryset
  

class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
  template_name = "leads/category_detail.html"
  context_object_name = "category"
  
  def get_context_data(self, **kwargs):
    context = super(CategoryDetailView, self).get_context_data(**kwargs)
    leads = self.get_object().leads.all()
    context.update({
      "leads": leads
    })
    return context
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Category.objects.filter(
        organisation = user.userprofile
      )
    else:
      queryset = Category.objects.filter(
        organisation = user.agent.organisation
      )  
    return queryset
  
class CategoryCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
  template_name = "leads/category_create.html"
  form_class = CategoryModelForm
  
  def get_success_url(self):
    return reverse("leads:category-list")
  
  def form_valid(self, form):
    category = form.save(commit=False)
    category.organisation = self.request.user.userprofile
    category.save()
    return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
  template_name = "leads/category_update.html"
  form_class = CategoryModelForm
  
  def get_success_url(self):
    return reverse("leads:category-list")
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Category.objects.filter(
        organisation = user.userprofile
      )
    else:
      queryset = Category.objects.filter(
        organisation = user.agent.organisation
      )
    return queryset

class CategoryDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
  template_name = "leads/category_delete.html"
  
  def get_success_url(self):
    return reverse("leads:category-list")
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Category.objects.filter(
        organisation = user.userprofile
      )
    else:
      queryset = Category.objects.filter(
        organisation = user.agent.organisation
      )
    return queryset
  
  
   
class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
  template_name = "leads/lead-category-update.html"
  form_class = LeadCategoryUpdateForm
  
  def get_queryset(self):
    user = self.request.user
    if user.is_organisor:
      queryset = Lead.objects.filter(organisation=user.userprofile)
    else:
      queryset = Lead.objects.filter(organisation=user.agent.organisation)
      queryset = queryset.filter(agent__user=user)
    return queryset
  
  def get_success_url(self):
    return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})
  
  
  


# def lead_list(request):
#   leads = Lead.objects.all()
#   context = {
#     "leads": leads
#   }
#   return render(request, "leads/lead_list.html", context)

# def lead_create(request):
#   form = LeadModelForm()
#   if request.method == "POST":
#     form = LeadModelForm(request.POST)
#     if form.is_valid():
#       form.save()
#       return redirect("/leads")
#   context = {
#     "form": form
#   }
#   return render(request, "leads/lead_create.html", context)

# def lead_update(request, pk):
#   lead = Lead.objects.get(id=pk)
#   form = LeadModelForm(instance=lead)
  
#   if request.method == "POST":
#     form = LeadModelForm(request.POST, instance=lead)
#     if form.is_valid():
#       form.save()
#       return redirect("/leads")
#   context = {
#     "lead": lead,
#     "form": form
#   }
#   return render(request, "leads/lead_update.html", context)

# def lead_update(request, pk):
#   lead = Lead.objects.get(id=pk)
#   form = LeadForm()
#   print(lead)
#   if request.method == "POST":
#     form = LeadForm(request.POST)
#     if form.is_valid():
#       first_name = form.cleaned_data['first_name']
#       last_name = form.cleaned_data['last_name']
#       age = form.cleaned_data['age']
      
#       lead.first_name = first_name
#       lead.last_name = last_name
#       lead.age = age
      
#       lead.save()
#       return redirect("/leads")
#   context = {
#     "lead": lead,
#     "form": form
#   }
#   return render(request, "leads/lead_update.html", context)

# def lead_create(request):
#   form = LeadForm()
#   if request.method == "POST":
#     form = LeadForm(request.POST)
#     if form.is_valid():
#       first_name = form.cleaned_data['first_name']
#       last_name = form.cleaned_data['last_name']
#       age = form.cleaned_data['age']
#       agent = Agent.objects.first()
#       Lead.objects.create(
#         first_name = first_name,
#         last_name = last_name,
#         age = age,
#         agent = agent
#       )
#       return redirect("/leads")
#   context = {
#     "form": form
#   }
#   return render(request, "leads/lead_create.html", context)
