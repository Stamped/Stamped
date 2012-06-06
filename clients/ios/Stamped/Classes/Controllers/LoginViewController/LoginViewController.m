//
//  LoginViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/23/12.
//
//

#import "LoginViewController.h"
#import "STStampedAPI.h"

@interface LoginLoadingView : UIView {
    UIActivityIndicatorView *_activityView;
}
@property(nonatomic,retain) UILabel *titleLabel;
@end

@interface LoginKeyboardButton : UIButton
@end

@interface LoginTextField : UITextField
@end

@interface LoginTextView : UIView {
    UITextField *_username;
    UITextField *_password;
}
@property (nonatomic, assign) id delegate;

- (void)setEditing:(BOOL)editing;
- (NSString*)username;
- (NSString*)password;


@end

@interface LoginViewController ()

@end

@implementation LoginViewController
@synthesize loading=_loading;
@synthesize delegate;

- (id)init {
    
    if ((self = [super init])) {
        
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];
        
    }
    return self;
    
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.view.backgroundColor = [UIColor clearColor];
    
    if (!_stampedImageView) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"stamped_login_blue.png"]];
        [self.view addSubview:imageView];
        [imageView release];
        _stampedImageView = imageView;
        
        UIImageView *corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_left.png"]];
        [self.view addSubview:corner];
        [corner release];
       
        corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_right.png"]];
        [self.view addSubview:corner];
        [corner release];
        
        CGRect frame = corner.frame;
        frame.origin.x = (self.view.bounds.size.width - corner.frame.size.width);
        corner.frame = frame;
        
    }

    if (!_textView) {
        LoginTextView *view = [[LoginTextView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height, self.view.bounds.size.width, 44.0f)];
        view.delegate = self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
        [self.view addSubview:view];
        [view release];
        _textView = view;
    }
    

}

- (void)viewDidUnload {
    _textView = nil;
    _stampedImageView = nil;
    [super viewDidUnload];
}


#pragma mark - Animations

- (void)animateIn {
    
    _stampedImageView.layer.shadowOpacity = 0.7f;
    _stampedImageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    _stampedImageView.layer.shadowRadius = 10;
    _stampedImageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:_stampedImageView.bounds].CGPath;

    [CATransaction begin];
    [CATransaction setAnimationDuration:0.4f];
    [CATransaction setCompletionBlock:^{
        
        self.view.backgroundColor = [UIColor whiteColor];
        _stampedImageView.layer.shadowOpacity = 0.0f;
        
        [UIView animateWithDuration:0.3f animations:^{
            CGRect frame = _textView.frame;
            frame.origin.y = self.view.bounds.size.height - 44.0f;
            _textView.frame = frame;
        }];
        
    }];
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position"];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    animation.fromValue = [NSValue valueWithCGPoint:CGPointMake(_stampedImageView.layer.position.x, -_stampedImageView.bounds.size.height/2)];
    [_stampedImageView.layer addAnimation:animation forKey:nil];
    
    [CATransaction commit];
    
}

- (void)animateOut {
    
    _stampedImageView.layer.shadowOpacity = 0.0f;
    _stampedImageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    _stampedImageView.layer.shadowRadius = 10.0f;
    _stampedImageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:_stampedImageView.bounds].CGPath;
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:0.4f];
    [CATransaction setCompletionBlock:^{
        
        if ([(id)delegate respondsToSelector:@selector(loginViewControllerDidDismiss:)]) {
            [self.delegate loginViewControllerDidDismiss:self];
        }
        
    }];
    
    CGPoint toPos = CGPointMake(_stampedImageView.layer.position.x, -_stampedImageView.bounds.size.height/2);
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"position"];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    animation.fromValue = [NSValue valueWithCGPoint:_stampedImageView.layer.position];
    animation.toValue = [NSValue valueWithCGPoint:toPos];
    [_stampedImageView.layer addAnimation:animation forKey:nil];
    _stampedImageView.layer.position = toPos;
    [CATransaction commit];
    

}


#pragma mark - Login Methods

- (void)login {
    
    NSString* login = [_textView username];
    NSString* password = [_textView password];
    [[STStampedAPI sharedInstance] loginWithScreenName:login password:password andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {

        if (error) {

            UIAlertView *alertView = [[UIAlertView alloc] initWithTitle:@"Couldn't Log In" message:@"The username and password do not match." delegate:(id<UIAlertViewDelegate>)self cancelButtonTitle:@"Reset password" otherButtonTitles:@"      OK      ", nil];
            [alertView show];
            [alertView release];
            
        } else {
            
            [self animateOut];
            
        }
        
    }];
    
}


#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    _loading = loading;

    if (_loading) {
        
        if (!_loadingView) {

            LoginLoadingView *view = [[LoginLoadingView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height-82.0f, self.view.bounds.size.width, 60.0f)];
            [self.view addSubview:view];
            [view release];
            _loadingView = view;
            _loadingView.titleLabel.text = [NSString stringWithFormat:@"@%@", [_textView username]];
            
        }
        
    } else {
        
        if (_loadingView) {
            [_loadingView removeFromSuperview], _loadingView=nil;
        }
        
    }
    
}


#pragma mark - Keyboard Notifications

- (void)keyboardWillShow:(NSNotification*)notification {
    
    UIWindow *window = nil;
    
    for (UIWindow *aWindow in [[UIApplication sharedApplication] windows]) {
        if ([aWindow isKindOfClass:NSClassFromString(@"UITextEffectsWindow")]) {
            window = aWindow;
            break;
        }
    }
    
    if (window && !_loginButton) {
                
        LoginKeyboardButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
        UIImage *image = [UIImage imageNamed:@"login_keyboard_btn.png"];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        image = [UIImage imageNamed:@"login_keyboard_btn_disabled.png"];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateDisabled];
        button.frame = CGRectMake(floorf(window.bounds.size.width - 78.0f), floorf(window.bounds.size.height - (image.size.height+1.0f)), 76.0f, image.size.height);
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:14];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.7f] forState:UIControlStateNormal];
        [button setTitle:@"Login" forState:UIControlStateNormal];
        [button addTarget:self action:@selector(loginButtonHit:) forControlEvents:UIControlEventTouchUpInside];
        [window addSubview:button];
        _loginButton = button;

    }

    CGFloat duration = [[[notification userInfo] objectForKey:UIKeyboardAnimationDurationUserInfoKey] integerValue];
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:duration animations:^{
        _textView.layer.transform = CATransform3DMakeTranslation(0.0f, -keyboardFrame.size.height, 0);
        _stampedImageView.layer.transform = CATransform3DMakeTranslation(0.0f, -keyboardFrame.size.height, 0);
    }];

}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    if (_loginButton) {
        [_loginButton removeFromSuperview];
        _loginButton=nil;
    }
    [UIView animateWithDuration:0.25f animations:^{
        _textView.layer.transform = CATransform3DMakeTranslation(0.0f, _textView.bounds.size.height, 0);;
        _stampedImageView.layer.transform = CATransform3DIdentity;        
    }];;
    
}


#pragma mark - LoginTextView Actions

- (void)loginButtonHit:(id)sender {
    
    [_textView setEditing:NO];
    [self setLoading:YES];
    
    double delayInSeconds = 0.6f;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [self login];
    });
    
    
}

- (void)cancel:(LoginTextView*)view {
    [view setEditing:NO];
    [self animateOut];
}


#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    
    if (alertView.cancelButtonIndex == buttonIndex) {
        
        // reset password
        
        
    } else {
        
        [_textView setEditing:YES];
        
    }
    
}

@end

#pragma mark - LoginTextView

@implementation LoginTextView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
                
        self.backgroundColor = [UIColor clearColor];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[[UIImage imageNamed:@"login_text_bg.png"] stretchableImageWithLeftCapWidth:1.0f topCapHeight:0.0f]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:imageView];
        [imageView release];
        
        CGRect frame = imageView.frame;
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        
        UIImage *image = [UIImage imageNamed:@"login_close_button.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        [button setImage:image forState:UIControlStateNormal];
        [button addTarget:self action:@selector(cancel:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        
        frame = button.frame;
        frame.size = image.size;
        frame.origin.y = ((self.bounds.size.height - frame.size.height) / 2) + 1.5f;
        frame.origin.x = (self.bounds.size.width - (frame.size.width+4.0f));
        button.frame = frame;
        
        image = [UIImage imageNamed:@"login_text_gutter.png"];
        CGFloat height = image.size.height;
        
        LoginTextField *textField = [[LoginTextField alloc] initWithFrame:CGRectMake(4.0f, floorf((self.bounds.size.height-height)/2)+1.0f, 133.0f, height)];
        textField.delegate = (id<UITextFieldDelegate>)self;
        textField.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];
        textField.font = [UIFont systemFontOfSize:14];
        textField.placeholder = @"Username";
        textField.keyboardAppearance = UIKeyboardAppearanceAlert;
        textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        textField.autocorrectionType = UITextAutocorrectionTypeNo;
        textField.returnKeyType = UIReturnKeyNext;
        [textField setBackground:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        [self addSubview:textField];
        [textField release];
        _username = textField;
        
        textField = [[LoginTextField alloc] initWithFrame:CGRectMake(floorf(CGRectGetMaxX(textField.frame) + 6.0f), floorf((self.bounds.size.height-height)/2)+1.0f, 133.0f, height)];
        textField.delegate = (id<UITextFieldDelegate>)self;
        textField.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];
        textField.placeholder = @"Password";
        textField.keyboardAppearance = UIKeyboardAppearanceAlert;
        textField.secureTextEntry = YES;
        textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        textField.autocorrectionType = UITextAutocorrectionTypeNo;
        textField.returnKeyType = UIReturnKeyDone;
        [textField setBackground:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        [self addSubview:textField];
        [textField release];
        _password = textField;
        
    }
    return self;
}


#pragma mark - Setters

- (void)setEditing:(BOOL)editing {
    
    if (editing) {
        
        [_username becomeFirstResponder];
        
    } else {
        
        [self endEditing:YES];
        
    }
    
}


#pragma mark - Getters

- (NSString*)username {
    return _username.text;
}

- (NSString*)password {
    return _password.text;
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    [self.delegate cancel:self];
    
}

@end


#pragma mark - LoginTextField

@implementation LoginTextField

- (CGRect)textRectForBounds:(CGRect)bounds {
    bounds.origin.y += 8.0f;
    bounds.origin.x += 8.0f;
    bounds.size.width -= 16.0f;
    return bounds;
}

- (CGRect)placeholderRectForBounds:(CGRect)bounds {
    bounds.origin.y += 8.0f;
    bounds.origin.x += 8.0f;
    bounds.size.width -= 16.0f;
    return bounds;
}

- (CGRect)editingRectForBounds:(CGRect)bounds {
    bounds.origin.y += 8.0f;
    bounds.origin.x += 8.0f;
    bounds.size.width -= 16.0f;
    return bounds;
}

- (CGRect)clearButtonRectForBounds:(CGRect)bounds {
    return bounds;
}

- (void)drawPlaceholderInRect:(CGRect)rect {
    
    rect.origin.x += 2.0f;
    [[UIColor colorWithRed:0.769f green:0.769f blue:0.769f alpha:1.0f] setFill];
    [self.placeholder drawInRect:rect withFont:[UIFont systemFontOfSize:13]];
    
}


@end


#pragma mark - LoginKeyboardButton

@implementation LoginKeyboardButton

- (id)buttonWithType:(UIButtonType)type {
    
    UIButton *button = [UIButton buttonWithType:type];
    
    UIImage *image = [UIImage imageNamed:@"login_keyboard_btn.png"];
    [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
    
    image = [UIImage imageNamed:@"login_keyboard_btn_disabled.png"];
    [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateDisabled];

    button.frame = CGRectMake(0.0f, 300.0f, 100.0f, image.size.height);
    
    return button;
    
}

@end


#pragma mark - LoginLoadingView

@implementation LoginLoadingView

@synthesize titleLabel;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
        view.frame = CGRectMake((self.bounds.size.width-18.0f)/2, (self.bounds.size.height-18.0f)/2, 18.0f, 18.0f);
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        [self addSubview:view];
        [view release];
        _activityView = view;
        [_activityView startAnimating];
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-font.lineHeight, self.bounds.size.width, font.lineHeight)];
        label.backgroundColor = [UIColor clearColor];
        label.font = font;
        label.textAlignment = UITextAlignmentCenter;
        label.textColor = [UIColor colorWithWhite:0.749f alpha:1.0f];
        label.shadowColor = [UIColor colorWithWhite:1.0f alpha:0.6f];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:label];
        [label release];
        self.titleLabel = label;
        
    }
    return self;
    
}

- (void)dealloc {
    self.titleLabel = nil;
    [super dealloc];
}

@end

