from rest_framework.routers import DefaultRouter

from apps.api_v0.views.access import AccessModelViewSet
from apps.api_v0.views.camera import CameraModelViewSet
from apps.api_v0.views.lock import ElectronicLockModelViewSet
from apps.api_v0.views.people import PeopleModelViewSet

router = DefaultRouter()

router.register('camera', CameraModelViewSet, basename='camera')
router.register('electronic-lock', ElectronicLockModelViewSet, basename='electronic-lock')
router.register('people', PeopleModelViewSet, basename='people')
router.register('access', AccessModelViewSet, basename='access')
urlpatterns = router.urls