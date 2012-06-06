//
//  SocialSignupHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SocialSignupHeaderView.h"
#import "STAvatarView.h"

@implementation SocialSignupHeaderView
@synthesize titleLabel=_titleLabel;
@synthesize detailLabel=_detailLabel;
@synthesize subTitleLabel=_subTitleLabel;
@synthesize imageView=_imageView;
@synthesize stampView=_stampView;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
    
        STAvatarView *imageView = [[STAvatarView alloc] initWithFrame:CGRectMake(15.0f, 12.0f, 78.0f, 78.0f)];
        imageView.imageView.frame = CGRectInset(imageView.bounds, 4.0f, 4.0f);
        [self addSubview:imageView];
        _imageView = [imageView retain];
        [imageView release];
        [_imageView setDefault];
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectMake(imageView.bounds.size.width-20, -8, 28.0f, 28.0f)];
        stampView.size = STStampImageSize28;
        [imageView addSubview:stampView];
        _stampView = stampView;
        [stampView release];
        _stampView = [_stampView retain];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        label.font = [UIFont boldSystemFontOfSize:16];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.font = [UIFont systemFontOfSize:12];
        [self addSubview:label];
        _subTitleLabel = [label retain];
        [label release];
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f];
        label.font = [UIFont italicSystemFontOfSize:12];
        [self addSubview:label];
        _detailLabel = [label retain];
        [label release];
        
    }
    return self;
}

- (void)dealloc {
    [_subTitleLabel release], _subTitleLabel=nil;
    [_detailLabel release], _detailLabel=nil;
    [_titleLabel release], _titleLabel=nil;
    [_imageView release], _imageView=nil;
    [_stampView release], _stampView=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGFloat originX = CGRectGetMaxX(_imageView.frame) + 10.0f;
    CGFloat originY = CGRectGetMinY(_imageView.frame) + 10.0f;
    
    [_titleLabel sizeToFit];
    [_subTitleLabel sizeToFit];
    [_detailLabel sizeToFit];
    
    if (_titleLabel.text) {
        
        CGRect frame = _titleLabel.frame;
        frame.origin.x = originX;
        frame.origin.y = originY;
        _titleLabel.frame = frame;
        
        originY = CGRectGetMaxY(_titleLabel.frame) + 2.0f;
        
    }
    
    if (_subTitleLabel.text) {
        
        CGRect frame = _subTitleLabel.frame;
        frame.origin.x = originX;
        frame.origin.y = originY;
        _subTitleLabel.frame = frame;
        
        originY = CGRectGetMaxY(_subTitleLabel.frame) + 4.0f;
        
    }
    
    if (_detailLabel.text) {
        
        CGRect frame = _detailLabel.frame;
        frame.origin.x = originX;
        frame.origin.y = originY;
        _detailLabel.frame = frame;
        
    }
    
    
}

- (void)setStampColors:(NSArray*)colors {
    [_stampView setupWithColors:colors];
}

@end
