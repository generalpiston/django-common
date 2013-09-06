
from rest_framework import generics, mixins
from .exceptions import ActionMissingError, WrongActionError


__all__ = ['CreateAPIView', 'ListAPIView', 'RetrieveAPIView',
           'DestroyAPIView', 'UpdateAPIView', 'ListCreateAPIView',
           'RetrieveUpdateAPIView', 'RetrieveDestroyAPIView', 'RetrieveUpdateDestroyAPIView']


class ActionBasedGenericAPIView(generics.GenericAPIView):
  def get_allowed_actions(self):
    return []

  def initial(self, request, *args, **kwargs):
    super(ActionBasedGenericAPIView, self).initial(request, *args, **kwargs)
    if 'action' not in request.GET:
      raise ActionMissingError()
    elif request.GET['action'] not in self.get_allowed_actions():
      raise WrongActionError("Action isn't one of [%s]" % ','.join(self.get_allowed_actions()))


class CreateAPIView(mixins.CreateModelMixin,
                    ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['create']

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'create':
      return self.create(request, *args, **kwargs)
    else:
      raise WrongActionError()


class ListAPIView(mixins.ListModelMixin,
                  ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['list']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'list':
      return self.list(request, *args, **kwargs)
    else:
      raise WrongActionError()


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['retrieve']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'retrieve':
      return self.retrieve(request, *args, **kwargs)
    else:
      raise WrongActionError()


class DestroyAPIView(mixins.DestroyModelMixin,
                     ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['destroy']

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'destroy':
      return self.destroy(request, *args, **kwargs)
    else:
      raise WrongActionError()


class UpdateAPIView(mixins.UpdateModelMixin,
                    ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['update']

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'update':
      return self.update(request, *args, **kwargs)
    elif request.GET['action'] == 'patch':
      return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['create', 'list']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'list':
      return self.list(request, *args, **kwargs)
    else:
      raise WrongActionError()

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'create':
      return self.create(request, *args, **kwargs)
    else:
      raise WrongActionError()


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['retrieve', 'update']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'retrieve':
      return self.retrieve(request, *args, **kwargs)
    else:
      raise WrongActionError()

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'update':
      return self.update(request, *args, **kwargs)
    elif request.GET['action'] == 'patch':
      return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['retrieve', 'destroy']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'retrieve':
      return self.retrieve(request, *args, **kwargs)
    else:
      raise WrongActionError()

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'destroy':
      return self.destroy(request, *args, **kwargs)
    else:
      raise WrongActionError()


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   ActionBasedGenericAPIView):
  def get_allowed_actions(self):
    return ['retrieve', 'update', 'destroy']

  def get(self, request, *args, **kwargs):
    if request.GET['action'] == 'retrieve':
      return self.retrieve(request, *args, **kwargs)
    else:
      raise WrongActionError()

  def post(self, request, *args, **kwargs):
    if request.GET['action'] == 'update':
      return self.update(request, *args, **kwargs)
    elif request.GET['action'] == 'patch':
      return self.partial_update(request, *args, **kwargs)
    elif request.GET['action'] == 'destroy':
      return self.destroy(request, *args, **kwargs)
    else:
      raise WrongActionError()
