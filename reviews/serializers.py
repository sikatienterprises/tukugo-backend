from rest_framework import serializers
from reviews.models import RideRating, RideIssue,DriverSupportRequest


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

class DriverSupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverSupportRequest
        fields = ['id', 'message', 'created_at']