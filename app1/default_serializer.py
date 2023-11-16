from rest_framework_mongoengine import serializers

def getDefaultSerializer(class_name):
    class DefaultSerializer(serializers.DocumentSerializer):
        class Meta:
            model = class_name
            fields = '__all__'

    return DefaultSerializer
