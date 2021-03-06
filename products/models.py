from decimal import Decimal
from unidecode import unidecode

from django.template import defaultfilters
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.shortcuts import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.humanize.templatetags.humanize import intcomma

from mptt.models import MPTTModel, TreeForeignKey
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslationManager
from ckeditor_uploader.fields import RichTextUploadingField
from filer.fields.image import FilerImageField
from autoslug.fields import AutoSlugField
from colorfield.fields import ColorField


class Category(MPTTModel, TranslatableModel):
    parent = TreeForeignKey('self', null=True, blank=True,)
    translations = TranslatedFields(
        name=models.CharField(max_length=60, verbose_name=_('Name')),
        slug=models.SlugField(verbose_name=_('Slug'), unique=True,),
    )
    order = models.IntegerField(default=0)
    objects = TranslationManager()

    def __str__(self):
        return "{}".format(self.safe_translation_getter('name'))

    class MPTTMeta:
        level_attr = 'mptt_level'

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=self)
        except:
            ancestors = []
        else:
            ancestors = [i.slug for i in ancestors]
        slugs = []
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[i + 1]))
        return slugs

    def get_absolute_url(self):
        return reverse_lazy('products:product_list', args=[self.safe_translation_getter('slug')])

    @property
    def get_related_products(self):
        cats = [self.pk]
        if self.get_children():
            for child in self.get_children():
                cats.append(child.pk)
        return Product.objects.filter(category__in=cats)

    @property
    def get_related_four_products(self):
        cats = [self.pk]
        if self.get_children():
            for child in self.get_children():
                cats.append(child.pk)
        return Product.objects.filter(category__in=cats)[0:4]


class Color(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=60)
    )
    color = ColorField()

    def __str__(self):
        return "{}".format(self.safe_translation_getter('name'))


class Size(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=60)
    )

    def __str__(self):
        return "{}".format(self.safe_translation_getter('name'))


class Brands(models.Model):
    name = models.CharField(max_length=60, verbose_name=_('Name'))
    logo = FilerImageField(null=True, verbose_name=_('Logo'))
    category = TreeForeignKey(Category, null=True,)

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')

    def __str__(self):
        return "{}".format(self.name)


class ProductImage(models.Model):
    file = FilerImageField(verbose_name=_('Image'), null=True)
    product = models.ForeignKey('Product', verbose_name=_('Product'), related_name='images')


class Product(models.Model):
    def get_populate_from(self):
        return defaultfilters.slugify(unidecode(self.name))

    def get_slugify(value):
        return value.replace(' ', '-')

    name = models.CharField(max_length=120, verbose_name=_('Product name'), )
    category = TreeForeignKey(Category, verbose_name=_('Category'), )
    brand = models.ForeignKey(Brands, verbose_name=_('Brand'), )
    description = RichTextUploadingField(blank=True, null=True, verbose_name=_('Description'), )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Product Owner'), related_name='products', )
    created_at = models.DateField(auto_now_add=True)
    available_in_stock = models.BooleanField(default=True, verbose_name=_('Available in stock'))
    is_recommended = models.BooleanField(default=False)
    price = models.DecimalField(default=Decimal(1), decimal_places=2, max_digits=10, verbose_name=_('Price'), )
    is_sale = models.BooleanField(default=False)
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    slug = AutoSlugField(populate_from=get_populate_from,
                         unique_with=['owner__first_name', 'created_at'],
                         slugify=get_slugify,
                         always_update=True,
                         null=True, )
    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        return "{}".format(self.name)

    def get_default_image(self):
        return self.images.first()

    def get_all_images(self):
        return self.images.all()

    def get_price(self):
        currency = _('soum')
        return "{} {}".format(intcomma(int(self.price)), currency)

    def get_reviews(self):
        return self.product_reviews.filter(is_approved=True)

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.category.slug, self.slug])

    @property
    def get_related_products(self):
        return Product.objects.filter(category_id=self.category.id)

    def get_sale_price(self):
        try:
            sale = Sale.objects.first()
            sale_percent = sale.percent
        except Sale.DoesNotExist:
            sale_percent = 1
        sale_price = self.price * sale_percent / 100
        return self.price - sale_price

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='product_reviews',)
    reviewer = models.CharField(max_length=120, )
    reviewer_location = models.CharField(max_length=120, blank=True, null=True, )
    subject = models.CharField(max_length=60)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True,)

    def __str__(self):
        return "{}".format(self.subject)


class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class Sale(models.Model):
    percent = models.IntegerField()