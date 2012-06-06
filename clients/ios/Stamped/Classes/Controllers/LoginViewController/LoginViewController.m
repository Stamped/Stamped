//
//  LoginViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/23/12.
//
//

#import "LoginViewController.h"
#import "STStampedAPI.h"

#define kStampBackgroundOffset 160
#define inOutAnimationDuration 0.45f

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
    LoginKeyboardButton *_loginButton;
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
        _didAnimateIn = NO;
        
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
        
        CGRect frame = _stampedImageView.frame;
        frame.origin.y = -kStampBackgroundOffset;
        _stampedImageView.frame = frame;
        
        UIImageView *corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_left.png"]];
        [self.view addSubview:corner];
        [corner release];
       
        corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_right.png"]];
        [self.view addSubview:corner];
        [corner release];
        
        frame = corner.frame;
        frame.origin.x = (self.view.bounds.size.width - corner.frame.size.width);
        corner.frame = frame;
        
    }

    if (!_textView) {
        LoginTextView *view = [[LoginTextView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height - (216.0f+44.0f), self.view.bounds.size.width, 44.0f)];
        view.delegate = self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
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
    
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:NO];
    [_textView setEditing:YES];
    [UIView setAnimationsEnabled:_enabled];
    
    UIWindow *window = nil;
    for (UIWindow *aWindow in [[UIApplication sharedApplication] windows]) {
        if ([aWindow isKindOfClass:NSClassFromString(@"UITextEffectsWindow")]) {
            window = aWindow;
            break;
        }
    }
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:inOutAnimationDuration];
    [CATransaction setCompletionBlock:^{
        self.view.backgroundColor = [UIColor whiteColor];
        _didAnimateIn = YES;
    }];
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"transform.translation.y"];
    animation.fromValue = [NSNumber numberWithFloat:self.view.bounds.size.height + 20.0f];
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    
    [_stampedImageView.layer addAnimation:animation forKey:nil];
    [_textView.layer addAnimation:animation forKey:nil];
    [window.layer addAnimation:animation forKey:nil];
    
    [CATransaction commit];
        
}

- (void)animateOut {
    
    self.view.backgroundColor = [UIColor clearColor];
    
    _stampedImageView.layer.shadowOpacity = 0.0f;
    _stampedImageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
    _stampedImageView.layer.shadowRadius = 10.0f;
    _stampedImageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:_stampedImageView.bounds].CGPath;
    
    [CATransaction begin];
    [CATransaction setAnimationDuration:inOutAnimationDuration];
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
        
        [UIView animateWithDuration:0.3f animations:^{
           
            CGRect frame = _stampedImageView.frame;
            frame.origin.y = 0.0f;
            _stampedImageView.frame = frame;
            
        }];
        
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
    
    if (!_didAnimateIn) {
        return;
    }
    
    CGFloat duration = [[[notification userInfo] objectForKey:UIKeyboardAnimationDurationUserInfoKey] floatValue];
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:duration animations:^{
        
        CGRect frame = _stampedImageView.frame;
        frame.origin.y = -kStampBackgroundOffset;
        _stampedImageView.frame = frame;
        
        frame = _textView.frame;
        frame.origin.y = (self.view.bounds.size.height - (keyboardFrame.size.height+_textView.bounds.size.height));
        _textView.frame = frame;

    }];
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    if (_animatingOut) {
        return;
    }
    
    [UIView animateWithDuration:0.25f animations:^{
       
        CGRect frame = _textView.frame;
        frame.origin.y = self.view.bounds.size.height;
        _textView.frame = frame;
        
    }];;
    
}


#pragma mark - LoginTextView Actions

- (void)loginButtonHit:(id)sender {
    
    [_textView setEditing:NO];
    [self setLoading:YES];
    
    _stampedImageView.image = [UIImage imageNamed:@"stamped_login_red.png"];
    
    double delayInSeconds = 0.6f;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [self login];
    });
    
    
}

- (void)cancel:(LoginTextView*)view {
   
    _animatingOut = YES;
    self.view.backgroundColor = [UIColor clearColor];
    
    UIWindow *window = nil;
    for (UIWindow *aWindow in [[UIApplication sharedApplication] windows]) {
        if ([aWindow isKindOfClass:NSClassFromString(@"UITextEffectsWindow")]) {
            window = aWindow;
            break;
        }
    }

    CGRect frame = window.frame;
    
    [UIView animateWithDuration:inOutAnimationDuration animations:^{
        
        CGRect frame = _textView.frame;
        CGFloat diff = (self.view.bounds.size.height + kStampBackgroundOffset);
        
        frame.origin.y += diff;
        _textView.frame = frame;
        
        frame = _stampedImageView.frame;
        frame.origin.y += diff;
        _stampedImageView.frame = frame;
        
        frame = window.frame;
        frame.origin.y += diff;
        window.frame = frame;
        
    } completion:^(BOOL finished) {
       
        BOOL _enabled = [UIView areAnimationsEnabled];
        [UIView setAnimationsEnabled:NO];
        window.frame = frame;
        [_textView setEditing:NO];
        [UIView setAnimationsEnabled:_enabled];
        
        if ([(id)delegate respondsToSelector:@selector(loginViewControllerDidDismiss:)]) {
            [self.delegate loginViewControllerDidDismiss:self];
        }
        
    }];
    

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
        frame.origin.x = (self.bounds.size.width - (frame.size.width+3.0f));
        button.frame = frame;
        
        image = [UIImage imageNamed:@"login_text_gutter.png"];
        CGFloat height = image.size.height;
        
        LoginTextField *textField = [[LoginTextField alloc] initWithFrame:CGRectMake(4.0f, floorf((self.bounds.size.height-height)/2)+1.0f, 133.0f, height)];
        [textField addTarget:self action:@selector(textFieldTextDidChange:) forControlEvents:UIControlEventEditingChanged];
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
        [textField addTarget:self action:@selector(textFieldTextDidChange:) forControlEvents:UIControlEventEditingChanged];
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
    
        if (_loginButton) {
            [_loginButton removeFromSuperview], _loginButton=nil;
        }
        
        [self endEditing:YES];
        
    }
    
}


#pragma mark - Getters

- (NSString*)username {
    
    if (_username.text) {
        return [_username.text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
    }
    
    return @"";
}

- (NSString*)password {
    
    if (_password.text) {
        return [_password.text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
    }
    
    return @"";
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    [self.delegate cancel:self];
    
}

- (void)login:(id)sender {
    
    [self.delegate loginButtonHit:sender];
    
}


#pragma mark - UITextFieldDelegate 

- (void)textFieldTextDidChange:(UITextField*)textField {
    
    if (_loginButton) {
        _loginButton.enabled = ([self username].length > 0 && [self password].length > 0);
    }
    
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    
    if (textField == _password) {
        if (_loginButton) {
            [_loginButton removeFromSuperview], _loginButton=nil;
        }
    }
    
}

- (void)textFieldDidBeginEditing:(UITextField *)textField {
    
    if (textField == _password) {
        
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
            [button setTitleColor:[UIColor colorWithRed:0.513f green:0.592f blue:0.694f alpha:1.0f] forState:UIControlStateDisabled];
            [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
            button.titleLabel.font = [UIFont boldSystemFontOfSize:17];
            button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
            [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.4f] forState:UIControlStateNormal];
            [button setTitle:@"Login" forState:UIControlStateNormal];
            [button addTarget:self action:@selector(login:) forControlEvents:UIControlEventTouchUpInside];
            [window addSubview:button];
            _loginButton.enabled = ([self username].length > 0 && [self password].length > 0);
            _loginButton = button;
            
        }

    } 
    
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    if (textField == _username) {
        [_password becomeFirstResponder];
    }
    
    return YES;
    
}

@end


#pragma mark - LoginTextField

@implementation LoginTextField

- (CGRect)textRectForBounds:(CGRect)bounds {
    bounds.origin.y += self.secureTextEntry ? 4.0f : 7.0f;
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
    bounds.origin.y += self.secureTextEntry ? 4.0f : 7.0f;
    bounds.origin.x += 8.0f;
    bounds.size.width -= 16.0f;
    return bounds;
}

- (CGRect)clearButtonRectForBounds:(CGRect)bounds {
    return bounds;
}

- (void)drawPlaceholderInRect:(CGRect)rect {
    
    rect.origin.x = floorf(rect.origin.x+2.0f);
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

