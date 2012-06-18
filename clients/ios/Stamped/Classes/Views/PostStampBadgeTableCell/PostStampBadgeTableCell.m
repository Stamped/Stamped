//
//  PostStampBadgeTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import "PostStampBadgeTableCell.h"

@implementation PostStampBadgeTableCell
@synthesize delegate;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if (self = [super initWithStyle:style reuseIdentifier:reuseIdentifier]) {
                
        UIImageView *imageView = [[UIImageView alloc] init];
        [self addSubview:imageView];
        _badgeImageView = imageView;
        [imageView release];
        
        UIFont *font = [UIFont systemFontOfSize:11];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = font;
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        [self addSubview:label];
        _titleLabel = label;
        [label release];
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.font = font;
        [self addSubview:label];
        _detailTitleLabel = label;
        [label release];
        
        font = [UIFont boldSystemFontOfSize:13];
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = font;
        label.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        [self addSubview:label];
        _midTitleLabel = label;
        [label release];
        
        UIImage *image = [UIImage imageNamed:@"post_stamp_share_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:@"Share" forState:UIControlStateNormal];
        [button setTitleColor:[UIColor colorWithWhite:0.6f alpha:1.0f]forState:UIControlStateNormal];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, 1.0f);
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleShadowColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [self addSubview:button];
        button.frame = CGRectMake(self.bounds.size.width - 65.0f, floorf((self.bounds.size.height-image.size.height)/2), 55.0f, image.size.height);
        [button addTarget:self action:@selector(share:) forControlEvents:UIControlEventTouchUpInside];
        
        _titleLabel.text = @"You're the";
        _midTitleLabel.text = @"1st of your friends";
        _detailTitleLabel.text = @"to stamp this";
        _badgeImageView.image = [UIImage imageNamed:@"post_stamp_first_friends.png"];

    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    [_detailTitleLabel sizeToFit];
    [_midTitleLabel sizeToFit];
    [_badgeImageView sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = 15.0f;
    _titleLabel.frame = frame;
    
    frame = _midTitleLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = CGRectGetMaxY(_titleLabel.frame);
    _midTitleLabel.frame = frame;
    
    frame = _detailTitleLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = CGRectGetMaxY(_midTitleLabel.frame);;
    _detailTitleLabel.frame = frame;

    frame = _badgeImageView.frame;
    frame.origin.x = 10.0f;
    frame.origin.y = floorf((self.bounds.size.height-frame.size.height)/2);
    _badgeImageView.frame = frame;
    
}

- (void)setupWithBadge:(id<STBadge>)badge {
    
    _titleLabel.text = @"You're the";
    _detailTitleLabel.text = @"to stamp this";
    if ([badge.genre isEqualToString:@"entity_first_stamp"]) {
        
        _midTitleLabel.text = @"1st on Stamped";
        _badgeImageView.image = [UIImage imageNamed:@"post_stamp_first_global.png"];
        
    } else if ([badge.genre isEqualToString:@"friends_first_stamp"]) {
        
        _midTitleLabel.text = @"1st of your friends";
        _badgeImageView.image = [UIImage imageNamed:@"post_stamp_first_friends.png"];

    } else if ([badge.genre isEqualToString:@"user_first_stamp"]) {
        
        _titleLabel.text = @"This is your";
        _midTitleLabel.text = @"1st Stamp";
        _detailTitleLabel.text = @"Welcome to Stamped!";
        _badgeImageView.image = [UIImage imageNamed:@"post_stamp_first_friends.png"];

    }
    
    [self setNeedsLayout];
    
}

- (void)showShadow:(BOOL)show {
    
    if (show) {
        
        if (!_shadowView) {
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"post_stamp_keyline_shadow.png"]];
            [self addSubview:imageView];
            
            CGRect frame = imageView.frame;
            frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
            imageView.frame = frame;
            [imageView release];
            _shadowView = imageView;
        }
        
        if (_borderView) {
            [_borderView removeFromSuperview];
            _borderView = nil;
        }
        
    } else {
        
        if (!_borderView) {
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(5.0f, 0.0f, self.bounds.size.width-10.0f, 1.0f)];
            view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
            [self addSubview:view];
            _borderView = view;
            [view release];
        }
        
        if (_shadowView) {
            [_shadowView removeFromSuperview];
            _shadowView = nil;
        }
        
    }

    
}


#pragma mark - Actions

- (void)share:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(postStampBadgeTableCellShare:)]) {
        [self.delegate postStampBadgeTableCellShare:self];
    }
    
}

@end
