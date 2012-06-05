//
//  FriendStatusButton.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "FriendStatusButton.h"

#define kGreenButton [UIImage imageNamed:@"nav_button_green.png"]
#define kGreenButtonHi [UIImage imageNamed:@"nav_button_green_hi.png"]

#define kWhiteButton [UIImage imageNamed:@"nav_button_white.png"]
#define kWhiteButtonHi [UIImage imageNamed:@"nav_button_white_hi.png"]

#define kFollowingIcon [UIImage imageNamed:@"following_check_icon.png"]

#define kButtonImageLeftCap 5

@implementation FriendStatusButton
@synthesize status=_status;
@synthesize loading=_loading;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        _status = -1;
        self.titleLabel.font = [UIFont boldSystemFontOfSize:11];
    }
    return self;
    
}

- (id)init {
    if (self = [self initWithFrame:CGRectZero]) {}
    return self;
}


#pragma mark - Setters

- (void)setStatus:(FriendStatus)status {
    if (_status == status) return; // avoid unnecessary button state changes
    _status = status;
    
    // reset button states
    [self setTitle:nil forState:UIControlStateNormal];
    [self setBackgroundImage:nil forState:UIControlStateNormal];
    [self setBackgroundImage:nil forState:UIControlStateHighlighted];
    self.enabled = YES;
    self.titleLabel.shadowOffset = CGSizeZero;
    
    // set new states
    switch (_status) {
        case FriendStatusNotFollowing: {
            [self setTitle:@"Follow" forState:UIControlStateNormal];
            [self setBackgroundImage:[kGreenButton stretchableImageWithLeftCapWidth:kButtonImageLeftCap topCapHeight:0.0f] forState:UIControlStateNormal];
            [self setBackgroundImage:[kGreenButtonHi stretchableImageWithLeftCapWidth:kButtonImageLeftCap topCapHeight:0.0f] forState:UIControlStateHighlighted];
            [self setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
            [self setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.2f] forState:UIControlStateNormal];
            self.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        }
            break;
        case FriendStatusFollowing: {
            self.enabled = NO;
            [self setImage:kFollowingIcon forState:UIControlStateNormal];
        }
            break;
        case FriendStatusRequestSent: 
        case FriendStatusInviteSent: {
            [self setTitle:@"Sent" forState:UIControlStateNormal];
            [self setTitleColor:[UIColor colorWithWhite:0.749f alpha:1.0f] forState:UIControlStateNormal];
            self.enabled = NO;
        }
            break;
        case FriendStatusInvite: {
            [self setTitle:@"Invite" forState:UIControlStateNormal];
            [self setBackgroundImage:[kWhiteButton stretchableImageWithLeftCapWidth:kButtonImageLeftCap topCapHeight:0.0f] forState:UIControlStateNormal];
            [self setBackgroundImage:[kWhiteButtonHi stretchableImageWithLeftCapWidth:kButtonImageLeftCap topCapHeight:0.0f] forState:UIControlStateHighlighted];
            [self setTitleColor:[UIColor colorWithWhite:0.349f alpha:1.0f] forState:UIControlStateNormal];
        }
            break;
            
        default:
            break;
    }
    
}

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    self.imageView.alpha = _loading ? 0.0f : 1.0f;
    self.titleLabel.alpha = _loading ? 0.0f : 1.0f;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorViewStyle style = UIActivityIndicatorViewStyleGray;
            if (_status == FriendStatusNotFollowing) {
                style = UIActivityIndicatorViewStyleWhite;
            }
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:style];
            view.frame = CGRectMake((self.bounds.size.width-20.0f)/2, (self.bounds.size.height-20.0f)/2, 20.0f, 20.0f);
            [self addSubview:view];
            [view release];
            _activityView = view;
            [_activityView startAnimating];
            
        }
        
    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview], _activityView=nil;
        }
        
    }
    
    
}

@end
