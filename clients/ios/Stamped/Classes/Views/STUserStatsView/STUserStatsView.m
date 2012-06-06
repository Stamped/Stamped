//
//  STUserStatsView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserStatsView.h"
#import "STSimpleUserDetail.h"

// 96 x 56

@interface STStatButton : UIControl {
    UIImageView *_background;
}
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,retain) UILabel *detailTitleLabel;
@end

@implementation STUserStatsView
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        CGFloat originX = 10.0f;
        CGFloat height = 59.0f;
        CGFloat width = 99.0f;
        CGFloat originY = (self.bounds.size.height - height)/2;
        
        STStatButton *button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        button.tag = STUserHeaderStatCredit;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        button.detailTitleLabel.text = @"credits";
        [self addSubview:button];
        [button release];
        _creditButton = button;
        
        originX += 101.0f;
        button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        button.tag = STUserHeaderStatFollowers;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        button.detailTitleLabel.text = @"followers";
        [self addSubview:button];
        [button release];
        _followersButton = button;
        
        originX += 101.0f;
        button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        button.tag = STUserHeaderStatFollowing;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        button.detailTitleLabel.text = @"following";
        [self addSubview:button];
        [button release];
        _followingButton = button;

    }
    return self;
}

- (void)setupWithUser:(STSimpleUserDetail *)user {
    
    if ([user respondsToSelector:@selector(numCredits)]) {
        _creditButton.titleLabel.text = [NSString stringWithFormat:@"%i", user.numCredits.integerValue];
    }
    if ([user respondsToSelector:@selector(numFriends)]) {
        _followingButton.titleLabel.text = [NSString stringWithFormat:@"%i", user.numFriends.integerValue];
    }
    if ([user respondsToSelector:@selector(numFollowers)]) {
        _followersButton.titleLabel.text = [NSString stringWithFormat:@"%i", user.numFollowers.integerValue];
    }
    
    [self.subviews makeObjectsPerformSelector:@selector(setNeedsLayout)];

}

- (void)buttonHit:(UIView*)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stUserStatsView:didSelectStat:)]) {
        [self.delegate stUserStatsView:self didSelectStat:sender.tag];
    }
    
}

- (void)dealloc {
    [super dealloc];
}

@end

@implementation STStatButton
@synthesize titleLabel;
@synthesize detailTitleLabel;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        UIImage *image = [UIImage imageNamed:@"user_header_stats_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self addSubview:imageView];
        [imageView release];
        _background = imageView;
        
        CGRect frame = imageView.frame;
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(14.0f, 34.0f, 0.0f, 0.0f)];
        label.font = [UIFont systemFontOfSize:10];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        [self addSubview:label];
        [label release];
        self.detailTitleLabel = label;
        
        label = [[UILabel alloc] initWithFrame:CGRectMake(14.0f, 12.0f, 0.0f, 0.0f)];
        label.font = [UIFont fontWithName:@"TitlingGothicFBComp-Light" size:25];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        [self addSubview:label];
        [label release];
        self.titleLabel = label;

    }
    return self;
    
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    [self.detailTitleLabel sizeToFit];
    
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    
    UIImage *image = [UIImage imageNamed:highlighted ? @"user_header_stats_bg_hi.png" : @"user_header_stats_bg.png"];
    _background.image = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
    
}

- (void)dealloc {
    self.titleLabel = nil;
    self.detailTitleLabel = nil;
    [super dealloc];
}

@end
