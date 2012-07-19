//
//  PostStampFriendView.m
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import "PostStampFriendView.h"
#import "STAvatarView.h"
#import "STStampedAPI.h"

@implementation PostStampFriendView
@synthesize user=_user;
@synthesize stamp;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

        self.backgroundColor = [UIColor whiteColor];
        
        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, self.bounds.size.width)];
        view.userInteractionEnabled = NO;
        [self addSubview:view];
        _avatarView = view;
        [view release];
        
        _avatarView.layer.shadowRadius = 2.0f;
        _avatarView.layer.shadowOpacity = 0.1f;
        _avatarView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.userInteractionEnabled = NO;
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithWhite:0.749f alpha:1.0f];
        label.font = [UIFont boldSystemFontOfSize:9];
        [self addSubview:label];
        _titleLabel = label;
        [label release];
        
    }
    return self;
}

- (void)dealloc {
    self.stamp = nil;
    [_user release], _user=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    CGRect frame = _titleLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = floorf(self.bounds.size.height - frame.size.height);
    _titleLabel.frame = frame;
    
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    
    _avatarView.highlighted = highlighted;
    
}

- (void)setupWithUser:(id<STUser>)user index:(NSInteger)index {
    
    [_user release], _user=nil;
    _user = [user retain];
    
    BOOL highlighted = NO;
    if (user) {
       highlighted = IS_CURRENT_USER(user.userID);
    }
    
    if (highlighted) {
       
        _titleLabel.textColor = [UIColor colorWithRed:0.427f green:0.8f blue:0.239f alpha:1.0f];
        if (!_borderView) {
            
            UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"post_stamp_friend_border.png"]];
            [self addSubview:view];
            _borderView = view;
            [view release];
            
            CGRect frame = _borderView.frame;
            frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
            frame.origin.y = 2.0f;
            _borderView.frame = frame;
            
        }
        
    } else {
        
        _titleLabel.textColor = [UIColor colorWithWhite:0.749f alpha:1.0f];
        if (_borderView) {
            [_borderView removeFromSuperview], _borderView=nil;
        }
        
    }
    
    if (user) {
        BOOL usedLocalImage = NO;
        if ([user.userID isEqualToString:[STStampedAPI sharedInstance].currentUser.userID]) {
            UIImage* localImage = [STStampedAPI sharedInstance].currentUserImage;
            if (localImage) {
                _avatarView.imageView.image = localImage;
                usedLocalImage = YES;
            }
        }
        if (!usedLocalImage) {
            _avatarView.imageURL = [NSURL URLWithString:user.imageURL];
        }
    }
    
    _titleLabel.text = [NSString stringWithFormat:@"%i", index];
    [self setNeedsLayout];
        
}


@end
