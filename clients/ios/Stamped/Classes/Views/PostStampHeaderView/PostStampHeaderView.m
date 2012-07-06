//
//  PostStampHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import "PostStampHeaderView.h"
#import "STAvatarView.h"
#import "UserStampView.h"
#import "STStampedAPI.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

@implementation PostStampHeaderView
@synthesize titleLabel=_titleLabel;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {

        self.backgroundColor = [UIColor clearColor];
        
        id <STUser> user = [[STStampedAPI sharedInstance] currentUser];
        STAvatarView *avatar = [[STAvatarView alloc] initWithFrame:CGRectMake(14.0f, 6.0f, 48.0f, 48.0f)];
        avatar.imageURL = [NSURL URLWithString:user.imageURL];
        [self addSubview:avatar];
        [avatar release];
        
        UserStampView *view = [[UserStampView alloc] initWithFrame:CGRectMake(0.0f, 22.0f, 18.0f, 18.0f)];
        view.size = STStampImageSize18;
        [view setupWithUser:user];
        [self addSubview:view];
        _stampView = view;
        [view release];

        UIFont *font = [UIFont stampedTitleFontWithSize:26];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(68.0f, 28.0f, 0.0f, font.lineHeight)];
        label.backgroundColor = self.backgroundColor;
        label.font = font;
        label.textColor = [UIColor stampedBlackColor];
        label.highlightedTextColor = [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
                
        font = [UIFont systemFontOfSize:11];
        label = [[UILabel alloc] initWithFrame:CGRectMake(68.0f, 12.0f, 0.0f, font.lineHeight)];
        label.backgroundColor = self.backgroundColor;
        label.text = @"You stamped";
        label.font = font;
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.highlightedTextColor = [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f];
        [self addSubview:label];
        [label sizeToFit];
        [label release];
    
    }
    return self;
}

- (void)dealloc {
    self.titleLabel=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(frame.size.width, self.bounds.size.width - (frame.origin.x+30.0f));
    _titleLabel.frame = frame;
    
    frame = _stampView.frame;
    frame.origin.x = CGRectGetMaxX(_titleLabel.frame) - 6.0f;
    _stampView.frame = frame;
    
}



@end
