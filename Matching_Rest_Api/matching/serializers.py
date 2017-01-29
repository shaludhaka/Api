from rest_framework import serializers



class PATTERNSerializer(serializers.Serializer):
    FirstFirstName = serializers.CharField(allow_blank=True,required=False,default='')
    FirstMiddleName =serializers.CharField(allow_blank=True,required=False,default='')
    FirstLastName = serializers.CharField(allow_blank=True,required=False,default='')
    SecondFirstName = serializers.CharField(allow_blank=True,required=False,default='')
    SecondMiddleName = serializers.CharField(allow_blank=True,required=False,default='')
    SecondLastName = serializers.CharField(allow_blank=True,required=False,default='')