from rest_framework import serializers
from django.db import transaction
from apps.services.models import (
    VendorService,
    ServicePackage,
    ServiceAddon,
    VendorServiceImage,
)
from apps.categories.models import Category, SubCategory


class VendorServiceImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = VendorServiceImage
        fields = ("id", "image")
        read_only_fields = ("id",)


class ServiceAddonSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ServiceAddon
        fields = ("id", "name", "price")


class ServicePackageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ServicePackage
        fields = ("id", "title", "description", "price")


class VendorServiceSerializer(serializers.ModelSerializer):
    packages = ServicePackageSerializer(many=True, read_only=True)
    addons = ServiceAddonSerializer(many=True, read_only=True)
    images = VendorServiceImageSerializer(many=True, read_only=True)
    vendor = serializers.CharField(source="vendor.business_name", read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VendorService
        fields = [
            "id",
            "vendor",
            "category",
            "subcategory",
            "name",
            "description",
            "pricing_type",
            "base_price",
            "min_booking_hours",
            "max_booking_hours",
            "min_booking_days_before_event",
            "max_booking_duration_days",
            "is_active",
            "rating",
            "total_bookings",
            "views",
            "created_at",
            "updated_at",
            "packages",
            "addons",
            "images",
        ]


class VendorServiceCreateUpdateSerializer(serializers.ModelSerializer):
    packages = ServicePackageSerializer(many=True, required=False)
    addons = ServiceAddonSerializer(many=True, required=False)
    images = VendorServiceImageSerializer(many=True, required=False)

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VendorService
        fields = [
            "id",
            "category",
            "subcategory",
            "name",
            "description",
            "pricing_type",
            "base_price",
            "min_booking_hours",
            "max_booking_hours",
            "min_booking_days_before_event",
            "max_booking_duration_days",
            "is_active",
            "packages",
            "addons",
            "images",
        ]
        read_only_fields = ("id",)

    def validate(self, attrs):
        pricing_type = attrs.get("pricing_type", getattr(self.instance, "pricing_type", None))
        packages = attrs.get("packages", None)
        base_price = attrs.get("base_price", getattr(self.instance, "base_price", None))

        if pricing_type == "package":
            if not packages and not (self.instance and self.instance.packages.exists()):
                raise serializers.ValidationError({"packages": "At least one package required for pricing_type 'package'."})

        if base_price is None or base_price < 0:
            raise serializers.ValidationError({"base_price": "Must be >= 0"})

        if pricing_type == "per_hour":
            if not attrs.get("min_booking_hours") and not (self.instance and self.instance.min_booking_hours):
                raise serializers.ValidationError({"min_booking_hours": "Required for per_hour pricing."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        packages_data = validated_data.pop("packages", [])
        addons_data = validated_data.pop("addons", [])
        images_data = validated_data.pop("images", [])

        request = self.context.get("request")
        if not request or not getattr(request.user, "vendor_profile", None):
            raise serializers.ValidationError("Authenticated vendor required to create service.")

        vendor_profile = request.user.vendor_profile
        validated_data["vendor"] = vendor_profile

        service = VendorService.objects.create(**validated_data)

        for pkg in packages_data:
            ServicePackage.objects.create(service=service, **pkg)

        for addon in addons_data:
            ServiceAddon.objects.create(service=service, **addon)

        for img in images_data:
            file_obj = img.get("image") if isinstance(img, dict) else img
            if file_obj:
                VendorServiceImage.objects.create(service=service, image=file_obj)

        return service

    @transaction.atomic
    def update(self, instance, validated_data):
        packages_data = validated_data.pop("packages", None)
        addons_data = validated_data.pop("addons", None)
        images_data = validated_data.pop("images", None)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if packages_data is not None:
            existing = {p.id: p for p in instance.packages.all()}
            incoming_ids = []
            for pkg in packages_data:
                pkg_id = pkg.get("id")
                if pkg_id and pkg_id in existing:
                    obj = existing[pkg_id]
                    obj.title = pkg.get("title", obj.title)
                    obj.description = pkg.get("description", obj.description)
                    obj.price = pkg.get("price", obj.price)
                    obj.save()
                    incoming_ids.append(pkg_id)
                else:
                    new = ServicePackage.objects.create(service=instance, **pkg)
                    incoming_ids.append(new.id)
            to_delete = [p.id for p in instance.packages.all() if p.id not in incoming_ids]
            if to_delete:
                ServicePackage.objects.filter(id__in=to_delete).delete()

        if addons_data is not None:
            existing = {a.id: a for a in instance.addons.all()}
            incoming_ids = []
            for addon in addons_data:
                addon_id = addon.get("id")
                if addon_id and addon_id in existing:
                    obj = existing[addon_id]
                    obj.name = addon.get("name", obj.name)
                    obj.price = addon.get("price", obj.price)
                    obj.save()
                    incoming_ids.append(addon_id)
                else:
                    new = ServiceAddon.objects.create(service=instance, **addon)
                    incoming_ids.append(new.id)
            to_delete = [a.id for a in instance.addons.all() if a.id not in incoming_ids]
            if to_delete:
                ServiceAddon.objects.filter(id__in=to_delete).delete()

        if images_data is not None:
            existing = {img.id: img for img in instance.images.all()}
            incoming_ids = []
            for img in images_data:
                img_id = img.get("id") if isinstance(img, dict) else None
                if img_id and img_id in existing:
                    incoming_ids.append(img_id)
                else:
                    file_obj = img.get("image") if isinstance(img, dict) else img
                    if file_obj:
                        new = VendorServiceImage.objects.create(service=instance, image=file_obj)
                        incoming_ids.append(new.id)
            to_delete = [i.id for i in instance.images.all() if i.id not in incoming_ids]
            if to_delete:
                VendorServiceImage.objects.filter(id__in=to_delete).delete()

        return instance
