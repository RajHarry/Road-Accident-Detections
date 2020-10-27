# Car Accident Detection Project
## Execution of the project

1. Get sports1m model weight:
    -  Download file https://github.com/adamcasson/c3d/releases/download/v0.1/sports1M_weights_tf.h5, rename and save in 'c3d/trained_models/c3d_sports1m.h5'
    
2. Start Django web app:
   ```
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic
   python manage.py runserver
   ```  
3. Open brower to `http://127.0.0.1:8000`.

## References

[1] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in surveillance videos,” in The IEEE Conference on
Computer Vision and Pattern Recognition (CVPR), Jun. 2018.

[2] D. Tran, L. Bourdev, R. Fergus, et al., “Learning spatiotemporal features with 3d convolutional networks,” in The IEEE
International Conference on Computer Vision (ICCV), Dec. 2015 .

   [realworld]: <https://arxiv.org/pdf/1801.04264.pdf>
   [c3d]: <https://arxiv.org/pdf/1412.0767.pdf>