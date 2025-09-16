from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, datetime
from .models import Service, Subscription, Cliente, CategoriaServicio, Payment

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para registro de usuarios"""
    email = forms.EmailField(required=True, label=_('Correo electrónico'))
    first_name = forms.CharField(max_length=30, required=True, label=_('Nombres'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Apellidos'))
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label=_('Teléfono'),
        help_text=_('Formato: +56912345678')
    )
    direccion = forms.CharField(
        max_length=255, 
        required=False, 
        label=_('Dirección'),
        widget=forms.Textarea(attrs={'rows': 3})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {
            'username': _('Nombre de usuario'),
            'password1': _('Contraseña'),
            'password2': _('Confirmar contraseña'),
        }
        help_texts = {
            'username': _('Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        
        if commit:
            user.save()
            
            # Crear el perfil de cliente
            Cliente.objects.create(
                usuario=user,
                telefono=self.cleaned_data.get('telefono', ''),
                direccion=self.cleaned_data.get('direccion', '')
            )
            
        return user

class SubscriptionForm(forms.ModelForm):
    """Formulario para crear y editar suscripciones"""
    
    # Campos para el cliente
    nombres = forms.CharField(
        max_length=100,
        required=True,
        label='Nombres',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombres del cliente'
        })
    )
    
    apellidos = forms.CharField(
        max_length=100,
        required=True,
        label='Apellidos',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos del cliente'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    class Meta:
        model = Subscription
        fields = [
            'cliente', 'service', 'price', 'payment_method',
            'start_date', 'end_date', 'payment_status', 'notes'
        ]
        widgets = {
            'cliente': forms.HiddenInput(),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre la suscripción'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('user', None)
        self.cliente_id = kwargs.pop('cliente_id', None)
        super().__init__(*args, **kwargs)
        
        # Si se proporciona un cliente_id, establecerlo
        if self.cliente_id:
            try:
                cliente = Cliente.objects.get(id=self.cliente_id)
                self.fields['cliente'].initial = cliente
                self.fields['nombres'].initial = cliente.nombres
                self.fields['apellidos'].initial = cliente.apellidos
                self.fields['email'].initial = cliente.email
                self.fields['telefono'].initial = cliente.telefono
            except Cliente.DoesNotExist:
                pass
        # Si es una edición, establecer valores iniciales
        elif self.instance and self.instance.pk:
            cliente = self.instance.cliente
            self.fields['nombres'].initial = cliente.nombres
            self.fields['apellidos'].initial = cliente.apellidos
            self.fields['email'].initial = cliente.email
            self.fields['telefono'].initial = cliente.telefono
        
        # Filtrar servicios activos
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        
        # Establecer el precio inicial si se proporciona un servicio
        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                service = Service.objects.get(id=service_id)
                self.fields['price'].initial = service.precio_base
            except (ValueError, Service.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.service:
            self.fields['price'].initial = self.instance.service.precio_base
        
        # Establecer fechas por defecto para nuevas suscripciones
        if not self.instance.pk:
            hoy = timezone.now().date()
            self.fields['start_date'].initial = hoy
            self.fields['end_date'].initial = hoy + timedelta(days=30)
            
        # Si el usuario no es superusuario, ocultar el campo de precio
        if not (self.current_user and self.current_user.is_superuser):
            self.fields['price'].widget = forms.HiddenInput()
            
        # Agregar clases CSS a los campos
        for field_name, field in self.fields.items():
            if field_name not in ['notes', 'cliente'] and not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        service = cleaned_data.get('service')
        
        # Validar fechas
        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'La fecha de expiración no puede ser anterior a la fecha de inicio')
        
        # Validar que el servicio esté activo
        if service and not service.is_active:
            self.add_error('service', 'No se puede suscribir a un servicio inactivo')
        
        return cleaned_data
        
    def save(self, commit=True):
        # Obtener o crear el cliente
        cliente = None
        if self.cliente_id:
            cliente = Cliente.objects.get(id=self.cliente_id)
        elif self.instance and self.instance.pk:
            cliente = self.instance.cliente
        else:
            # Crear un nuevo cliente
            cliente = Cliente.objects.create(
                nombres=self.cleaned_data.get('nombres', ''),
                apellidos=self.cleaned_data.get('apellidos', ''),
                email=self.cleaned_data.get('email', ''),
                telefono=self.cleaned_data.get('telefono', ''),
                creado_por=self.current_user if self.current_user else None
            )
        
        # Actualizar los datos del cliente
        if cliente:
            cliente.nombres = self.cleaned_data.get('nombres', cliente.nombres)
            cliente.apellidos = self.cleaned_data.get('apellidos', cliente.apellidos)
            cliente.email = self.cleaned_data.get('email', cliente.email)
            cliente.telefono = self.cleaned_data.get('telefono', cliente.telefono or '')
            cliente.save()
            
            # Asignar el cliente a la suscripción
            self.instance.cliente = cliente
        
        # Guardar la suscripción
        return super().save(commit=commit)


class PaymentForm(forms.ModelForm):
    """Formulario para registrar pagos de suscripciones"""
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'payment_status', 'payment_date', 'reference', 'notes']


class ClientWithSubscriptionForm(forms.ModelForm):
    """Formulario para crear un cliente con su primera suscripción"""
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        label='Servicio',
        required=True,
        help_text='Seleccione el servicio para la suscripción del cliente',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Cliente
        fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion', 'fecha_nacimiento', 'notas', 'is_active']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Asegurarse de que los campos tengan las clases CSS correctas
        for field_name, field in self.fields.items():
            if field_name != 'is_active' and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def save(self, commit=True):
        # Guardar el cliente
        cliente = super().save(commit=False)
        if self.user:
            cliente.creado_por = self.user
        if commit:
            cliente.save()
            
            # Crear la suscripción si se proporcionó un servicio
            service = self.cleaned_data.get('service')
            if service:
                Subscription.objects.create(
                    cliente=cliente,
                    service=service,
                    price=service.precio_base,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=30),
                    is_active=True
                )
        
        return cliente


class ServiceForm(forms.ModelForm):
    """Formulario para crear y editar servicios de streaming"""
    
    class Meta:
        model = Service
        fields = [
            'nombre', 'nombre_mostrar', 'descripcion', 'categoria', 'precio_base', 
            'tipo_suscripcion', 'max_dispositivos', 'calidad', 'idiomas', 
            'fecha_lanzamiento', 'pais_origen', 'sitio_web', 'icono', 'imagen', 'is_active'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'idiomas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Español, Inglés, Francés'}),
            'fecha_lanzamiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pais_origen': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://ejemplo.com'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'max_dispositivos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_suscripcion': forms.Select(attrs={'class': 'form-select'}),
            'calidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 4K, 1080p, 720p'}),
            'icono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: netflix, spotify'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar placeholders y clases CSS
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
            # Agregar placeholders específicos
            if field_name == 'nombre':
                field.widget.attrs.update({'placeholder': 'Nombre interno del servicio (sin espacios, usar guiones)'})
            elif field_name == 'nombre_mostrar':
                field.widget.attrs.update({'placeholder': 'Nombre para mostrar a los usuarios'})
            elif field_name == 'precio_base':
                field.widget.attrs.update({'step': '0.01', 'min': '0'})
            elif field_name == 'sitio_web':
                field.widget.attrs.update({'placeholder': 'https://ejemplo.com'})
            
            # Hacer que los campos requeridos sean más evidentes
            if field.required:
                field.widget.attrs.update({'required': 'required'})
    
    def save(self, commit=True):
        service = super().save(commit=False)
        
        # Si es un nuevo servicio, establecer el usuario que lo creó
        if not service.pk and self.user:
            service.creado_por = self.user
        
        if commit:
            service.save()
            
        return service
