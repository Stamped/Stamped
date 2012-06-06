//
//  STUserStatsView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserStatsView.h"

// 96 x 56

@interface STStatButton : UIControl
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,retain) UILabel *detailTitleLabel;
@end

@implementation STUserStatsView

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        CGFloat originX = 10.0f;
        CGFloat height = 59.0f;
        CGFloat width = 96.0f;
        CGFloat originY = (self.bounds.size.height - height)/2;
        
        STStatButton *button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        [self addSubview:button];
        [button release];
        _creditButton = button;
        
        originX += 100.0f;
        button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        [self addSubview:button];
        [button release];
        _followingButton = button;
        
        originX += 100.0f;
        button = [[STStatButton alloc] initWithFrame:CGRectMake(originX, originY, width, height)];
        [self addSubview:button];
        [button release];
        _followersButton = button;
        
    }
    return self;
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
        
        CGRect frame = imageView.frame;
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(4.0f, 30.0f, 0.0f, 0.0f)];
        label.font = [UIFont systemFontOfSize:10];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        [self addSubview:label];
        [label release];
        self.detailTitleLabel = label;
        
        label = [[UILabel alloc] initWithFrame:CGRectMake(4.0f, 10.0f, 0.0f, 0.0f)];
        label.font = [UIFont fontWithName:@"TitlingGothicFBComp-Light" size:35];
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

- (void)dealloc {
    self.titleLabel = nil;
    self.detailTitleLabel = nil;
    [super dealloc];
}

@end
