from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from projects.models import Project
from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from .base import STATUS
from .models import (
    Category, Field, NumericField, LookupField, LookupValue,
    MultipleLookupField, MultipleLookupValue
)
from .forms import CategoryCreateForm, FieldCreateForm
from .serializer import (
    CategorySerializer, FieldSerializer, LookupFieldSerializer
)


# ############################################################################
#
# Administration views
#
# ############################################################################

class CategoryList(LoginRequiredMixin, TemplateView):
    template_name = 'categories/category_list.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user

        context = super(CategoryList, self).get_context_data()
        context['project'] = Project.objects.as_admin(user, project_id)

        return context


class CategoryOverview(LoginRequiredMixin, TemplateView):
    template_name = 'categories/category_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        category = Category.objects.as_admin(
            user, project_id, category_id)

        context = super(CategoryOverview, self).get_context_data()
        context['category'] = category

        return context


class CategoryCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create Category page and creates the Category
    when POST is requested
    """
    form_class = CategoryCreateForm
    template_name = 'categories/category_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            CategoryCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def get_success_url(self):
        """
        Returns the redeirect URL after successful creation of the
        observation type
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:category_overview',
            kwargs={
                'project_id': project_id, 'category_id': self.object.id
            }
        )

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        data = form.cleaned_data

        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        category = Category.objects.create(
            project=project,
            creator=self.request.user,
            name=strip_tags(data.get('name')),
            description=strip_tags(data.get('description')),
            default_status=data.get('default_status'),
            create_grouping=(data.get('create_grouping') == 'True')
        )

        messages.success(self.request, "The category has been created.")
        return redirect(
            'admin:category_overview',
            project_id=project.id,
            category_id=category.id
        )


class CategorySettings(LoginRequiredMixin, TemplateView):
    """
    Displays the observation type detail page
    """
    template_name = 'categories/category_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        category = Category.objects.as_admin(
            user, project_id, category_id)
        return {
            'category': category,
            'admin': category.project.is_admin(user),
            'status_types': STATUS
        }

    def post(self, request, project_id, category_id):
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category')
        data = request.POST

        category.name = strip_tags(data.get('name'))
        category.description = strip_tags(data.get('description'))
        category.default_status = data.get('default_status')
        category.save()

        messages.success(self.request, "The category has been updated.")
        context['category'] = category
        return self.render_to_response(context)


class CategoryDisplay(LoginRequiredMixin, TemplateView):
    template_name = 'categories/category_display.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, **kwargs):
        user = self.request.user
        category = Category.objects.as_admin(
            user, project_id, category_id)
        return super(CategoryDisplay, self).get_context_data(
            category=category, **kwargs)

    def post(self, request, project_id, category_id):
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)
        data = request.POST
        symbol = request.FILES.get('symbol')

        if category is not None:
            category.colour = data.get('colour')

            if symbol is not None:
                category.symbol = symbol
            elif data.get('clear-symbol') == 'true':
                category.symbol = None

            category.save()

        messages.success(
            self.request, 'This display settings have been updated')
        context['category'] = category
        return self.render_to_response(context)


class CategoryDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, **kwargs):
        user = self.request.user
        category = Category.objects.as_admin(
            user, project_id, category_id)
        return super(CategoryDelete, self).get_context_data(
            category=category, **kwargs)

    def get(self, request, project_id, category_id):
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)

        if category is not None:
            category.delete()

            messages.success(self.request, "The category has been deleted.")
            return redirect('admin:category_list', project_id=project_id)

        return self.render_to_response(context)


class FieldCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create field page
    """
    form_class = FieldCreateForm
    template_name = 'categories/field_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, data=None, key_error=False, **kwargs):
        project_id = self.kwargs['project_id']
        category_id = self.kwargs['category_id']

        context = super(FieldCreate, self).get_context_data(**kwargs)

        context['category'] = Category.objects.as_admin(
            self.request.user, project_id, category_id
        )
        context['fieldtypes'] = Field.get_field_types()
        context['key_error'] = key_error
        if key_error:
            context['data'] = data
        return context

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        category_id = self.kwargs['category_id']
        data = form.cleaned_data
        category = Category.objects.as_admin(
            self.request.user, project_id, category_id)

        proposed_key = slugify(strip_tags(data.get('name')))
        suggested_key = proposed_key

        count = 1
        while category.fields.filter(key=suggested_key).exists():
            suggested_key = '%s-%s' % (proposed_key, count)
            count = count + 1

        field = Field.create(
            strip_tags(data.get('name')),
            suggested_key,
            strip_tags(data.get('description')),
            data.get('required'),
            category,
            self.request.POST.get('type')
        )

        if isinstance(field, NumericField):
            field.minval = self.request.POST.get('minval') or None
            field.maxval = self.request.POST.get('maxval') or None
        field.save()

        field_create_url = reverse(
            'admin:category_field_create',
            kwargs={
                'project_id': project_id,
                'category_id': category_id
            }
        )

        messages.success(
            self.request,
            mark_safe('The field has been created. <a href="%s">Add another '
                      'field.</a>' % field_create_url)
        )

        return redirect(
            'admin:category_field_settings',
            project_id=category.project.id,
            category_id=category.id,
            field_id=field.id
        )


class FieldSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the field detail page
    """
    template_name = 'categories/field_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, field_id,
                         **kwargs):
        user = self.request.user
        field = Field.objects.as_admin(
            user, project_id, category_id, field_id)
        context = super(FieldSettings, self).get_context_data(**kwargs)
        context['field'] = field
        context['status_types'] = STATUS
        context['fieldtypes'] = Field.get_field_types()

        return context

    def post(self, request, project_id, category_id, field_id):
        context = self.get_context_data(
            project_id,
            category_id,
            field_id
        )
        field = context.pop('field')
        data = request.POST

        field.name = strip_tags(data.get('name'))
        field.description = strip_tags(data.get('description'))
        field.required = data.get('required') or False

        if isinstance(field, NumericField):
            field.minval = data.get('minval') or None
            field.maxval = data.get('maxval') or None
        field.save()

        messages.success(self.request, "The field has been updated.")
        context['field'] = field
        return self.render_to_response(context)


class FieldDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, field_id, **kwargs):
        user = self.request.user
        field = Field.objects.as_admin(
            user, project_id, category_id, field_id)
        return super(FieldDelete, self).get_context_data(
            field=field, **kwargs)

    def get(self, request, project_id, category_id, field_id):
        context = self.get_context_data(project_id, category_id, field_id)
        field = context.pop('field', None)

        if field is not None:
            field.delete()

            messages.success(self.request, "The field has been deleted.")
            return redirect(
                'admin:category_overview',
                project_id=project_id,
                category_id=category_id
            )

        return self.render_to_response(context)


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class CategoryUpdate(APIView):
    """
    API Endpoints for a category in the AJAX API.
    /ajax/projects/:project_id/categories/:category_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id, format=None):
        category = Category.objects.as_admin(
            request.user, project_id, category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id, format=None):
        """
        Updates an category
        """

        category = Category.objects.as_admin(
            request.user, project_id, category_id)

        serializer = CategorySerializer(
            category, data=request.DATA, partial=True,
            fields=('id', 'name', 'description', 'status'))

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldUpdate(APIView):
    """
    API endpoints for fields
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id, field_id,
            format=None):
        """
        Updates a field
        """
        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)

        serializer = FieldSerializer(
            field, data=request.DATA, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldLookups(APIView):
    """
    API endpoint for lookupvalues
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id/lookupvalues
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id, field_id,
             format=None):
        """
        Adds a lookup value to the lookup field
        """
        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)
        name = strip_tags(request.DATA.get('name'))

        if isinstance(field, LookupField):
            LookupValue.objects.create(name=name, field=field)

            serializer = LookupFieldSerializer(field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif isinstance(field, MultipleLookupField):
            MultipleLookupValue.objects.create(name=name, field=field)

            serializer = LookupFieldSerializer(field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldLookupsUpdate(APIView):
    """
    API endpoint for lookupvalues
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id/lookupvalues/:value_id
    """
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, category_id, field_id,
               value_id, format=None):
        """
        Removes a LookupValue
        """
        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)

        if (isinstance(field, LookupField) or
                isinstance(field, MultipleLookupField)):
            field.lookupvalues.get(pk=value_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldsReorderView(APIView):
    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id, format=None):
        category = Category.objects.as_admin(
            request.user, project_id, category_id)
        try:
            category.re_order_fields(request.DATA.get('order'))

            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Field.DoesNotExist:
            return Response(
                {'error': 'One or more field ids where not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ############################################################################
#
# Public API views
#
# ############################################################################

class SingleCategory(APIView):
    """
    API endpoint for a single category
    /api/projects/:project_id/categories/:category_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id, format=None):
        """
        Returns the category and all fields
        """
        category = Category.objects.get_single(
            request.user, project_id, category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)
