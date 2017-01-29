from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from serializers import PATTERNSerializer
from rest_framework import generics
from utils import PatternMatch


class MatchData(generics.GenericAPIView):

    serializer_class = PATTERNSerializer

    def post(self, request, format=None):
        print request.data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
          ap_data = PatternMatch(serializer.data)
          response = ap_data.extract_values()
          return response
        return Response(serializer.errors)
