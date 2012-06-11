//
//  STSocialAuthViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import "STSocialAuthViewController.h"
#import "SignupWelcomeViewController.h"
#import "STAuth.h"
#import "STTwitter.h"
#import "STFacebook.h"

@interface STSocialAuthViewController ()
@property(nonatomic,readonly) SocialAuthType authType;
@property(nonatomic,assign) BOOL loading;
@end

@implementation STSocialAuthViewController
@synthesize authType=_authType;
@synthesize loading=_loading;
@synthesize delegate;

- (id)initWithAuthType:(SocialAuthType)type {
    
    if ((self = [super init])) {
        _authType = type;
        
        if (_authType == SocialAuthTypeTwitter) {
            
            [STEvents addObserver:self selector:@selector(twitterAuthFinished:) event:EventTypeTwitterAuthFinished];
            [STEvents addObserver:self selector:@selector(twitterAuthFailed:) event:EventTypeTwitterAuthFailed];

        } else if (_authType == SocialAuthTypeFacebook) {
            
            [STEvents addObserver:self selector:@selector(facebookAuthFinished:) event:EventTypeFacebookAuthFinished];
            [STEvents addObserver:self selector:@selector(facebookAuthFailed:) event:EventTypeFacebookAuthFailed];
            
        }
        
    }
    return self;
    
}

- (void)dealloc {
    [STEvents removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.navigationItem.hidesBackButton = YES;
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.view.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    [self.view addSubview:background];
    [background release];
    
    double delayInSeconds = 1.0f;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [self beginAuth];
    });
    
    [self setLoading:YES];

}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Auth

- (void)beginAuth {
    
    if (_authType == SocialAuthTypeTwitter) {
        
        [[STTwitter sharedInstance] auth];
         
    } else if (_authType == SocialAuthTypeFacebook) {
        
        [[STFacebook sharedInstance] auth];
        
    }
    
}


#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
            [self.view addSubview:view];
            [view startAnimating];
            [view release];
            _activityView = view;
            
            view.frame = CGRectMake((self.view.bounds.size.width-20.0f)/2, (self.view.bounds.size.height-30.0f)/2, 20.0f, 20.0f);
            
        }
        
    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview], _activityView=nil;
        }
        
    }
    
}


#pragma mark - Sign up

- (void)signupTwitter {
    
    [STEvents removeObserver:self];
    [[STTwitter sharedInstance] getTwitterUser:^(id user, NSError *error) {
        
        if (user && !error) {
            [[STTwitter sharedInstance] setTwitterUser:user];
            SignupWelcomeViewController *controller = [[SignupWelcomeViewController alloc] initWithType:SignupWelcomeTypeTwitter];
            controller.navigationItem.hidesBackButton = YES;
            double delayInSeconds = 0.1f;
            dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
            dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
                [self.navigationController pushViewController:controller animated:YES];
                [controller release];
            });
        }
        
    }];
    
}

- (void)signupFacebook {
    
    [STEvents removeObserver:self];
    [[STFacebook sharedInstance] loadMe];
    [[STFacebook sharedInstance] setHandler:^(NSDictionary *dictionary) {
                
        SignupWelcomeViewController *controller = [[SignupWelcomeViewController alloc] initWithType:SignupWelcomeTypeFacebook];
        controller.navigationItem.hidesBackButton = YES;
        double delayInSeconds = 0.1f;
        dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
        dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
            [self.navigationController pushViewController:controller animated:YES];
            [controller release];
        });
        
    }];
    
}


#pragma mark - Twitter Notifications 

- (void)twitterAuthFinished:(NSNotification*)notification {

    [[STAuth sharedInstance] twitterAuthWithToken:[[STTwitter sharedInstance] twitterToken] secretToken:[[STTwitter sharedInstance] twitterTokenSecret] completion:^(NSError *error) {
    
        if (error) {
                        
            [self signupTwitter];
            
        } else {
            
            if ([(id)delegate respondsToSelector:@selector(socialAuthViewControllerFinished:)]) {
                [self.delegate socialAuthViewControllerFinished:self];
            }
            
        }
        
    }];
    
}

- (void)twitterAuthFailed:(NSNotification*)notification {
    
    UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Twitter Failed" message:@"Twitter auth failed" delegate:(id<UIAlertViewDelegate>)self cancelButtonTitle:@"OK" otherButtonTitles:nil];
    [alert show];
    [alert release];
    
}


#pragma mark - Facebook Notifications

- (void)facebookAuthFinished:(NSNotification*)notification {
    
    [[STAuth sharedInstance] facebookAuthWithToken:[[[STFacebook sharedInstance] facebook] accessToken] completion:^(NSError *error) {
        
        if (error) {
            
            [self signupFacebook];
            
        } else {
            
            if ([(id)delegate respondsToSelector:@selector(socialAuthViewControllerFinished:)]) {
                [self.delegate socialAuthViewControllerFinished:self];
            }
            
        }
        
    }];
    
}

- (void)facebookAuthFailed:(NSNotification*)notification {
    
    UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Facebook Failed" message:@"Facebook auth failed" delegate:(id<UIAlertViewDelegate>)self cancelButtonTitle:@"OK" otherButtonTitles:nil];
    [alert show];
    [alert release];

}


#pragma mark - UIAlertViewDelegate 

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    
    if ([(id)delegate respondsToSelector:@selector(socialAuthViewControllerFailed:)]) {
        [self.delegate socialAuthViewControllerFailed:self];
    }
    
}


@end
