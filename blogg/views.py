from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, BlogUploadForm, CommentForm
from .models import Profile, Blog, User, Subscribers, Follow, Comment, Like
from cloudinary.forms import cl_init_js_callbacks
from django.core.exceptions import ObjectDoesNotExist
# from .email import send_welcome_email


def index(request):
    blog = Blog.objects.all()
    comments = Comment.objects.all()
    users = User.objects.exclude(id=request.user.id)
    
    return render(request, 'index.html', {"blogs":blog[::-1], "users": users, "comments": comments })

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data['email']
            recipient = Subscribers(name = username,email =email)
            recipient.save()
            # send_welcome_email(username,email)
            messages.success(request, f'Successfully created account created for {username}! Please log in to continue')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    # profile = Profile.objects.create(user=request.user)
    blog = request.user.profile.images.all()
    comments = Comment.objects.all()
    return render(request, 'users/profile.html', {"blog":blog[::-1], "comments": comments})

@login_required
def update(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Successfully updated your account!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/update.html', context)

def blog(request,blog_id):
    try:
        blog = Blog.objects.get(id = blog_id)
        comment = Comment.objects.all()
    except ObjectDoesNotExist:
        raise Http404()
    return render(request,"blog.html", {"blog":blog,"comment":comment})

@login_required
def search_results(request):
    if 'query' in request.GET and request.GET["query"]:
        search_term = request.GET.get("query")
        searched_blog= Blog.search_blog(search_term)
        message = f"{search_term}"
        return render(request, 'search.html', {"message":message,"blogs": searched_blog})
    else:
        message = "You haven't searched for any profile"
    return render(request, 'search.html', {'message': message})

def like_post(request):
    user = request.user
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        img_obj = Blog.objects.get(id = image_id)
        if user in img_obj.liked.all():
            img_obj.liked.remove(user)
        else:
            img_obj.liked.add(user)
        like, created = Like.objects.get_or_create(user = user, image_id = image_id)
        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        like.save()
    return redirect(request, 'index.html')

@login_required
def user_profile(request, username):
    user_prof = get_object_or_404(User, username=username)
    if request.user == user_prof:
        return redirect('profile', username=request.user.username)
    user_blogs= user_prof.profile.blogs.all()
    followers = Follow.objects.filter(followed=user_prof.profile)
    follow_status = None
    for follower in followers:
        if request.user.profile == follower.follower:
            follow_status = True
        else:
            follow_status = False
    params = {
        'user_prof': user_prof,
        'user_blogs': user_blogs,
        'followers': followers,
        'follow_status': follow_status
    }
    print(followers)
    return render(request, 'users/user_profile.html', params)

def follow(request, to_follow):
    if request.method == 'GET':
        user_profile3 = Profile.objects.get(pk=to_follow)
        follow_s = Follow(follower=request.user.profile, followed=user_profile3)
        follow_s.save()
        return redirect('user_profile', user_profile3.user.username)

def unfollow(request, to_unfollow):
    if request.method == 'GET':
        user_profile2 = Profile.objects.get(pk=to_unfollow)
        unfollow_d = Follow.objects.filter(follower=request.user.profile, followed=user_profile2)
        unfollow_d.delete()
        return redirect('user_profile', user_profile2.user.username)

@login_required 
def comment(request,blog_id):
        current_user=request.user
        blog = Blog.objects.get(id=blog_id)
        user_profile = User.objects.get(username=current_user.username)
        comments = Comment.objects.all()
        if request.method == 'POST':
                form = CommentForm(request.POST, request.FILES)
                if form.is_valid():
                        comment = form.save(commit=False)
                        comment.blogs = blog
                        comment.user = current_user
                        comment.save()  
                return redirect('index')
        else:
                form = CommentForm()
        return render(request, 'comment.html',locals())
@login_required
def upload_blog(request):
    blog = Blog.objects.all()
    comments = Comment.objects.all()
    users = User.objects.exclude(id=request.user.id)
    if request.method == "POST":
        form = BlogUploadForm(request.POST,request.FILES)
        if form.is_valid():
            blog = form.save(commit = False)
            blog.user = request.user.profile
            blog.save()
            messages.success(request, f'Successfully uploaded your pic!')
            return redirect('index')
    else:
        form = BlogUploadForm()
    return render(request, 'upload_blog.html', { "form": form, "users": users, })
