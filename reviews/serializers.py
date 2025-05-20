from rest_framework import serializers
from .models import RideRating, RideIssue


class RideRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRating
        fields = ['ride', 'driver', 'rating', 'feedback']

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


class RideIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideIssue
        fields = ['ride', 'issue','driver']

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)
