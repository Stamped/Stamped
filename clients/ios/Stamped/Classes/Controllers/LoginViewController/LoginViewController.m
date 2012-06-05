//
//  LoginViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/23/12.
//
//

#import "LoginViewController.h"
#import "STStampedAPI.h"

@interface LoginKeyboardButton : UIButton
@end

@interface LoginTextField : UITextField
@end

@interface LoginTextView : UIView {
    UITextField *_username;
    UITextField *_password;
}
- (void)setEditing:(BOOL)editing;

- (NSString*)_tempScreenName;
- (NSString*)_tempPassword;

@property (nonatomic, assign) id delegate;

@end

@interface LoginViewController ()

@end

@implementation LoginViewController
@synthesize loading=_loading;

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
    
    self.view.backgroundColor = [UIColor whiteColor];
    
    if (!_stampedImageView) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"Default.png"]];
        [self.view addSubview:imageView];
        [imageView release];
        _stampedImageView = imageView;
        
        CGRect frame = imageView.frame;
        frame.origin.y = -200.0f;
        imageView.frame = frame;
        
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
        LoginTextView *view = [[LoginTextView alloc] initWithFrame:CGRectMake(0.0f, self.view.bounds.size.height - 44.0f, self.view.bounds.size.width, 44.0f)];
        view.delegate = self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
        [self.view addSubview:view];
        [view release];
        _textView = view;
    }
    
    [_textView setEditing:YES];

}

- (void)viewDidUnload {
    _textView = nil;
    _stampedImageView = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];    
}


#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    
    
    
}

- (void)loginButtonClicked:(id)notImportant {
    NSString* login = _textView._tempScreenName;
    NSString* password = _textView._tempPassword;
    [[STStampedAPI sharedInstance] loginWithScreenName:login password:password andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {
        [_textView setEditing:NO];
        [self dismissModalViewControllerAnimated:YES];
    }];
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
        [button addTarget:self action:@selector(loginButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
        [window addSubview:button];
        _loginButton = button;

    }

    CGFloat duration = [[[notification userInfo] objectForKey:UIKeyboardAnimationDurationUserInfoKey] integerValue];
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:duration animations:^{
        _textView.layer.transform = CATransform3DMakeTranslation(0.0f, -keyboardFrame.size.height, 0);
    }];

}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    if (_loginButton) {
        [_loginButton removeFromSuperview];
        _loginButton=nil;
    }
    [UIView animateWithDuration:0.25f animations:^{
        _textView.layer.transform = CATransform3DIdentity;
    }];;
    
}


#pragma mark - LoginTextView Actions

- (void)cancel:(LoginTextView*)view {
    [view setEditing:NO];
    [self dismissModalViewControllerAnimated:YES];
    
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
        frame.origin.y = (self.bounds.size.height - frame.size.height) / 2;
        frame.origin.x = (self.bounds.size.width - (frame.size.width+10.0f));
        button.frame = frame;
        
        image = [UIImage imageNamed:@"login_text_gutter.png"];
        CGFloat height = image.size.height;
        
        LoginTextField *textField = [[LoginTextField alloc] initWithFrame:CGRectMake(10.0f, (self.bounds.size.height-height)/2, 120.0f, height)];
        textField.placeholder = @"Username";
        textField.keyboardAppearance = UIKeyboardAppearanceAlert;
        textField.returnKeyType = UIReturnKeyDone;
        [textField setBackground:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        [self addSubview:textField];
        [textField release];
        _username = textField;
        
        textField = [[LoginTextField alloc] initWithFrame:CGRectMake(CGRectGetMaxX(textField.frame) + 10.0f, (self.bounds.size.height-height)/2, 120.0f, height)];
        textField.placeholder = @"Password";
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
        
        if ([_username isFirstResponder]) {
            [_username resignFirstResponder];
        }
        if ([_password isFirstResponder]) {
            [_password resignFirstResponder];
        }
        
    }
    
}


#pragma mark - Getters

- (NSString*)username {
    return _username.text;
}

- (NSString*)password {
    return _password.text;
}

- (NSString *)_tempScreenName {
    return [self username];
}

- (NSString *)_tempPassword {
    return [self password];
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
    bounds.origin.x += 4.0f;
    return bounds;
}

- (CGRect)placeholderRectForBounds:(CGRect)bounds {
    bounds.origin.y += 8.0f;
    bounds.origin.x += 4.0f;
    return bounds;
}

- (CGRect)editingRectForBounds:(CGRect)bounds {
    bounds.origin.y += 8.0f;
    bounds.origin.x += 4.0f;
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
