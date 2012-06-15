//
//  CreateEditView.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "CreateEditView.h"
#import "STAvatarView.h"

@interface CreateCreditToolbar : UIControl
@end
@interface CreateCaptureMenuButton : UIButton
@end
@interface CreateExpandedToolBar : UIImageView
@property(nonatomic,assign) UIButton *cameraButton;
- (id)initWithFrame:(CGRect)frame delegate:(id)delegate;
@end
@interface CreateExpandedCaptureMenu : UIImageView
- (id)initWithFrame:(CGRect)frame delegate:(id)delegate;
@end

@implementation CreateEditView
@synthesize textView=_textView;
@synthesize scrollView=_scrollView;
@synthesize avatarView=_avatarView;
@synthesize imageView=_imageView;
@synthesize editing=_editing;
@synthesize delegate;
@synthesize dataSource;
@synthesize keyboardType=_keyboardType;
@synthesize creditToolbar=_creditToolbar;
@synthesize tapGesture  = _tapGesture;

@synthesize menuView=_menuView;
@synthesize toolbar=_toolbar;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        UIScrollView *scrollView = [[UIScrollView alloc] initWithFrame:self.bounds];
        scrollView.contentInset = UIEdgeInsetsMake(0.0f, 0.0f, 10.0f, 0.0f);
        scrollView.backgroundColor = [UIColor whiteColor];
        scrollView.alwaysBounceVertical = YES;
        [self addSubview:scrollView];
        self.scrollView = scrollView;
        
        UITextView *textView = [[UITextView alloc] initWithFrame:CGRectMake(68.0f, 14.0f, self.bounds.size.width - 88.0f, 20.0f)];
        textView.font = [UIFont systemFontOfSize:12];
        textView.keyboardAppearance = UIKeyboardAppearanceAlert;
        textView.editable = NO;
        textView.delegate = (id<UITextViewDelegate>)self;
        textView.scrollEnabled = NO;
        [self.scrollView addSubview:textView];
        self.textView = textView;
        [textView release];
        
       // self.textView.layer.borderColor = [UIColor redColor].CGColor;
       // self.textView.layer.borderWidth = 1.0f;
    
        STUploadingImageView *imageView = [[STUploadingImageView alloc] initWithFrame:CGRectMake((self.bounds.size.width-200.0f)/2, 100.0f, 200.0f, 200.0f)];
        
        //imageView.layer.borderWidth = 1.0f;
        //imageView.layer.borderColor = [UIColor redColor].CGColor;
        
        self.imageView.contentMode = UIViewContentModeScaleAspectFit;
        [self.scrollView addSubview:imageView];
        self.imageView = imageView;
        [imageView release];
        
        id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
        STAvatarView *avatar = [[STAvatarView alloc] initWithFrame:CGRectMake(10.0f, 10.0f, 48.0f, 48.0f)];
        avatar.imageURL = [NSURL URLWithString:user.imageURL];
        [self.scrollView addSubview:avatar];
        self.avatarView = avatar;
        self.avatarView.alpha = 0.0f;
        [avatar release];
    
        UIImage *image = [UIImage imageNamed:@"round_btn_bg.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor colorWithWhite:0.349f alpha:1.0f] forState:UIControlStateNormal];
        [button setTitle:@"Add a comment" forState:UIControlStateNormal];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        button.frame = CGRectMake((self.bounds.size.width-200.0f)/2, 60.0f, 200.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [self.scrollView addSubview:button];
        [button addTarget:self action:@selector(comment:) forControlEvents:UIControlEventTouchUpInside];
        _commentButton = button;
        
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor colorWithWhite:0.349f alpha:1.0f] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"camera_icon_small.png"] forState:UIControlStateNormal];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        button.frame = CGRectMake((self.bounds.size.width-85.0f)/2, 110.0f, 85.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [self.scrollView addSubview:button];
        [button addTarget:self action:@selector(capture:) forControlEvents:UIControlEventTouchUpInside];
        _captureButton = button;
        
        CreateExpandedToolBar *toolbar = [[CreateExpandedToolBar alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height, self.bounds.size.width, 0) delegate:self];
        toolbar.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:toolbar];
        self.toolbar = toolbar;
        [toolbar release];
        self.toolbar.hidden = YES;
        
        CreateExpandedCaptureMenu *view = [[CreateExpandedCaptureMenu alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height+44, self.bounds.size.width, 0.0f) delegate:self];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:view];
        self.menuView = view;;
        [view release];
        self.menuView.hidden = YES;
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self.scrollView addGestureRecognizer:gesture];
        [gesture release];
        
        CreateCreditToolbar *creditToolbar = [[CreateCreditToolbar alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-50.0f, self.bounds.size.width, 50.0f)];
        creditToolbar.backgroundColor = [UIColor whiteColor];
        [creditToolbar addTarget:self action:@selector(creditPicker:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:creditToolbar];
        [creditToolbar release];
        self.creditToolbar = creditToolbar;
        
    }
    return self;
}

- (void)dealloc {
    self.textView = nil;
    self.avatarView = nil;
    self.imageView = nil;
    self.toolbar = nil;
    self.menuView = nil;
    self.scrollView = nil;
    [super dealloc];
}

- (void)layoutScrollView {
    
    CGSize size = self.scrollView.contentSize;
    if (self.imageView.image) {
        
        CGRect frame = self.imageView.frame;
        frame.origin.y = MAX(100.0f, CGRectGetMaxY(self.textView.frame)+10.0f);
        self.imageView.frame = frame;
        size.height = CGRectGetMaxY(self.imageView.frame) + 10.0f;
        
    } else {
        size.height = CGRectGetMaxY(self.textView.frame) + 10.0f;
    }
    size.height = MAX(size.height, self.bounds.size.height);
    if (size.height != self.scrollView.contentSize.height) {
        self.scrollView.contentSize = size;
    }
    
}


#pragma mark - State Handling

- (void)updateState {
    
    if (_editing) {

        self.textView.hidden = NO;
        _captureButton.hidden = YES;
        _commentButton.hidden = YES;
        
    } else {
        
        self.textView.hidden = ![self.textView hasText];
        _captureButton.hidden = (self.imageView.image!=nil);
        _commentButton.hidden = !self.textView.hidden;
        
    }
    self.avatarView.alpha = self.textView.hidden ? 0.0f : 1.0f;
    self.textView.editable = _editing;
    
}


#pragma mark - Setters

- (void)setEditing:(BOOL)editing {
    if (_editing == editing) return;
    if (![(id)dataSource respondsToSelector:@selector(createEditViewSuperview:)]) return;
    _editing=editing;

    UIView *expandView = [self.dataSource createEditViewSuperview:self];
        
    if (_editing) {
        
        __block CGRect frame = [self convertRect:self.scrollView.frame toView:expandView];
        [expandView addSubview:self];
        self.frame = expandView.bounds;
        self.scrollView.frame = frame;
        
        self.toolbar.hidden = NO;
        self.menuView.hidden = (_keyboardType==CreateEditKeyboardTypeText);
        self.creditToolbar.hidden = YES;
        
        frame = _toolbar.frame;
        frame.origin.y = self.bounds.size.height;
        _toolbar.frame = frame;
        
        frame = _menuView.frame;
        frame.origin.y = self.bounds.size.height + _toolbar.bounds.size.height;
        _menuView.frame = frame;
        
        self.backgroundColor = [UIColor clearColor];
        [UIView animateWithDuration:0.25f animations:^{
            
            frame.origin.y = _editing ? 20.0f : 0.0f; // status bar offset
            self.scrollView.frame = frame;
            
            CGRect frame = _toolbar.frame;
            frame.size.width = self.bounds.size.width;
            frame.origin.y = self.bounds.size.height - (_menuView.bounds.size.height+frame.size.height);
            _toolbar.frame = frame;
            
            frame = _menuView.frame;
            frame.size.width = self.bounds.size.width;
            frame.origin.y = self.bounds.size.height - frame.size.height;
            _menuView.frame = frame;
            
            [self updateState];

        } completion:^(BOOL finished) {
            
            self.scrollView.clipsToBounds = !_editing;
            self.backgroundColor = [UIColor whiteColor];
            
        }];
        
        
    } else {
        
        [self.textView resignFirstResponder];
        self.scrollView.clipsToBounds = !_editing;

        __block CGRect frame = [expandView.superview convertRect:expandView.frame toView:self];
        self.backgroundColor = [UIColor clearColor];
        
        [UIView animateWithDuration:0.25f animations:^{
           
            self.scrollView.frame = CGRectInset(frame, 5, 10.0f);
            
            CGRect frame = _toolbar.frame;
            frame.origin.y = self.bounds.size.height;
            _toolbar.frame = frame;
            
            frame = _menuView.frame;
            frame.origin.y = self.bounds.size.height + _toolbar.bounds.size.height;
            _menuView.frame = frame;
            
            [self updateState];

        } completion:^(BOOL finished) {
            
            [expandView addSubview:self];
            self.frame = CGRectInset(expandView.bounds, 5, 10.0f);
            self.scrollView.frame = self.bounds;
            
            self.toolbar.hidden = YES;
            self.menuView.hidden = YES;
            self.backgroundColor = [UIColor whiteColor];

            self.creditToolbar.hidden = NO;
            self.creditToolbar.alpha = 0.0f;
            
            [UIView animateWithDuration:0.1f animations:^{
                self.creditToolbar.alpha = 1.0f;
            }];

        }];

        
    }
    
    
    
}

- (void)setKeyboardType:(CreateEditKeyboardType)keyboardType {
    _keyboardType=keyboardType;
    
    _menuView.hidden = keyboardType!=CreateEditKeyboardTypePhoto;
    _toolbar.cameraButton.selected = (_keyboardType==CreateEditKeyboardTypePhoto);
    
    if (keyboardType==CreateEditKeyboardTypePhoto) {
        [self.textView resignFirstResponder];
    } else {
        [self.textView becomeFirstResponder];
    }
    
}


#pragma mark - Actions

- (void)creditPicker:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createEditViewSelectedCreditPicker:)]) {
        [self.delegate createEditViewSelectedCreditPicker:self];
    }
    
}

- (void)comment:(id)sender {
    
    [self setEditing:YES];
    self.keyboardType = CreateEditKeyboardTypeText;

}

- (void)capture:(id)sender {
    
    self.keyboardType = CreateEditKeyboardTypePhoto;
    [self setEditing:YES];

}

- (void)done:(id)sender {
    
    [self setEditing:NO];
    
}

- (void)photo:(UIButton*)sender {
    
    [sender setSelected:![sender isSelected]];

    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:NO];
    self.keyboardType = [sender isSelected] ? CreateEditKeyboardTypePhoto : CreateEditKeyboardTypeText;
    [UIView setAnimationsEnabled:_enabled];
    
}

- (void)capturePhoto:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createEditView:addPhotoWithSourceType:)]) {
        [self.delegate createEditView:self addPhotoWithSourceType:UIImagePickerControllerSourceTypeCamera];
    }
    
}

- (void)choosePhoto:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(createEditView:addPhotoWithSourceType:)]) {
        [self.delegate createEditView:self addPhotoWithSourceType:UIImagePickerControllerSourceTypePhotoLibrary];
    }
    
}

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    if (!_editing) {
        
        [self setEditing:YES];
        self.keyboardType = CreateEditKeyboardTypeText;

    } else {
        
        BOOL _enabled = [UIView areAnimationsEnabled];
        [UIView setAnimationsEnabled:NO];
        self.keyboardType = CreateEditKeyboardTypeText;
        [UIView setAnimationsEnabled:_enabled];
        
    }

}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    if (!_editing && [self.textView hasText]) {
        
        CGRect rect = self.bounds;
        rect.size.height -= 50.0f;
        CGPoint point = [gestureRecognizer locationInView:self];
        
        if (CGRectContainsPoint(rect, point)) {
            return !CGRectContainsPoint(_captureButton.frame, point);
        }
        
        return NO;
        
    }
    

    return (self.keyboardType==CreateEditKeyboardTypePhoto);
    
}


#pragma mark - UITextViewDelegate

- (BOOL)textViewShouldBeginEditing:(UITextView *)textView {
    return YES;
}

- (BOOL)textViewShouldEndEditing:(UITextView *)textView {
    return YES;
}

- (void)textViewDidBeginEditing:(UITextView *)textView {
    
}

- (void)textViewDidEndEditing:(UITextView *)textView {
    
}

- (void)textViewDidChange:(UITextView *)textView {
    
    CGRect frame = textView.frame;
    if(frame.size.height != textView.contentSize.height) {
        frame.size.height = textView.contentSize.height;
    }
    textView.frame = frame;
    [self layoutScrollView];
    
}

@end


#pragma mark CreateCaptureMenuButton

@implementation CreateCaptureMenuButton

- (CGRect)titleRectForContentRect:(CGRect)contentRect {
    
    CGSize size = [[self titleForState:UIControlStateNormal] sizeWithFont:[UIFont boldSystemFontOfSize:14]];
    return CGRectMake((contentRect.size.width-size.width)/2, contentRect.size.height - 32.0f, size.width, size.height);
    
}

- (CGRect)imageRectForContentRect:(CGRect)contentRect {
    
    CGSize size = [[self imageForState:UIControlStateNormal] size];
    return CGRectMake((contentRect.size.width-size.width)/2, ((contentRect.size.height-size.height)/2) - 12.0f, size.width, size.height);
    
}

@end


#pragma mark - CreateExpandedCaptureMenu

@implementation CreateExpandedCaptureMenu

- (id)initWithFrame:(CGRect)frame delegate:(id)delegate {
    UIImage *image = [UIImage imageNamed:@"create_kb_bg.png"];
    frame.size.height = image.size.height;
    if ((self = [super initWithFrame:frame])) {
        
        self.userInteractionEnabled = YES;
        self.image =[image stretchableImageWithLeftCapWidth:1 topCapHeight:0];
        
        image = [UIImage imageNamed:@"create_kb_btn.png"];
        CreateCaptureMenuButton *button = [CreateCaptureMenuButton buttonWithType:UIButtonTypeCustom];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:@"Take photo" forState:UIControlStateNormal];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:14]];
        [button.titleLabel setShadowOffset:CGSizeMake(0.0f, 1.0f)];
        [button setTitleColor:[UIColor colorWithWhite:0.2789f alpha:1.0f] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:1.0f alpha:0.2f] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"create_kb_camera_icon.png"] forState:UIControlStateNormal];
        [self addSubview:button];
        [button addTarget:delegate action:@selector(capturePhoto:) forControlEvents:UIControlEventTouchUpInside];
        
        CGRect frame = CGRectMake(2.0f, 10.0f, self.bounds.size.width-4.0f, image.size.height);
        button.frame = frame;
        
        button = [CreateCaptureMenuButton buttonWithType:UIButtonTypeCustom];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:@"Choose photo" forState:UIControlStateNormal];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:14]];
        [button.titleLabel setShadowOffset:CGSizeMake(0.0f, 1.0f)];
        [button setTitleColor:[UIColor colorWithWhite:0.2789f alpha:1.0f] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:1.0f alpha:0.2f] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"create_kb_photo_icon.png"] forState:UIControlStateNormal];
        [self addSubview:button];
        [button addTarget:delegate action:@selector(choosePhoto:) forControlEvents:UIControlEventTouchUpInside];
        
        frame.origin.y = image.size.height + 12.0f;
        button.frame = frame;
        
    }
    return self;
}

@end


#pragma mark - CreateExpandedToolbar

@implementation CreateExpandedToolBar
@synthesize cameraButton;

- (id)initWithFrame:(CGRect)frame delegate:(id)delegate {
    UIImage *image = [UIImage imageNamed:@"login_text_bg.png"];
    frame.size.height = image.size.height;
    if ((self = [super initWithFrame:frame])) {
        
        self.userInteractionEnabled = YES;
        self.image =[image stretchableImageWithLeftCapWidth:1 topCapHeight:0];
        
        image = [UIImage imageNamed:@"create_toolbar_blue_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:@"Done" forState:UIControlStateNormal];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
        [button.titleLabel setShadowOffset:CGSizeMake(0.0f, -1.0f)];
        [button setTitleColor:[UIColor colorWithWhite:1.0f alpha:1.0f] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.1f] forState:UIControlStateNormal];
        [self addSubview:button];
        button.frame = CGRectMake(self.bounds.size.width - 60.0f, ((self.bounds.size.height-image.size.height)/2)+2.0f, 58.0f, image.size.height);
        [button addTarget:delegate action:@selector(done:) forControlEvents:UIControlEventTouchUpInside];
        
        image = [UIImage imageNamed:@"create_toolbar_capture_bg.png"];
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        image = [UIImage imageNamed:@"create_toolbar_capture_bg_hi.png"];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateSelected];
        [button setImage:[UIImage imageNamed:@"create_toolbar_capture_icon.png"] forState:UIControlStateNormal];
        UIImage *imageHI = [UIImage imageNamed:@"create_toolbar_capture_icon_hi.png"];
        [button setImage:imageHI forState:UIControlStateSelected];
        [self addSubview:button];
        button.frame = CGRectMake(2.0f, ((self.bounds.size.height-image.size.height)/2)+2.0f, 64.0f, image.size.height);
        [button addTarget:delegate action:@selector(photo:) forControlEvents:UIControlEventTouchUpInside];
        self.cameraButton = button;
        
    }
    return self;
}

@end


#pragma mark - CreateCreditToolbar

@implementation CreateCreditToolbar

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_picker_header_icon.png"]];
        [self addSubview:imageView];
        CGRect frame = imageView.frame;
        frame.origin.x = 10.0f;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        imageView.frame = frame;
        [imageView release];
        
        UIImage *shadow = [UIImage imageNamed:@"create_credit_shadow.png"];
        imageView = [[UIImageView alloc] initWithImage:[shadow stretchableImageWithLeftCapWidth:1 topCapHeight:0]];
        [self addSubview:imageView];
        frame = imageView.frame;
        frame.size.width = self.bounds.size.width;
        frame.origin.y = -shadow.size.height;
        imageView.frame = frame;
        [imageView release];

        UIFont *font = [UIFont systemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(40.0f, floorf((self.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.font = font;
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.backgroundColor = self.backgroundColor;
        label.text = @"Who deserves credit?";
        [self addSubview:label];
        [label sizeToFit];
        [label release];
        
    }
    return self;
    
}

@end
