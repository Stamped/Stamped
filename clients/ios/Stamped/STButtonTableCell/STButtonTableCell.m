//
//  STButtonTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import "STButtonTableCell.h"

@implementation STButtonTableCell
@synthesize titleLabel=_titleLabel;
@synthesize detailTitleLabel=_detailTitleLabel;
@synthesize delegate;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
    
        self.selectionStyle = UITableViewCellSelectionStyleNone;
        
        UIView *view = [[UIView alloc] init];
        self.backgroundView = view;
        [view release];
        
        UIImage *image = [UIImage imageNamed:@"round_btn_bg.png"];
        UIImage *imageHi = [UIImage imageNamed:@"round_btn_bg_hi.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleWidth;
        button.frame = CGRectMake(10.0f, 0.0f, self.bounds.size.width-20.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setBackgroundImage:[imageHi stretchableImageWithLeftCapWidth:(imageHi.size.width/2) topCapHeight:0] forState:UIControlStateHighlighted];
        [self addSubview:button];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
    
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.textAlignment = UITextAlignmentRight;
        label.userInteractionEnabled = NO;
        label.adjustsFontSizeToFitWidth = YES;
        label.minimumFontSize = 9;
        label.highlightedTextColor = [UIColor whiteColor];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleRightMargin;
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont systemFontOfSize:12];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        [button addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.userInteractionEnabled = NO;
        label.highlightedTextColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleRightMargin;
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont systemFontOfSize:12];
        [button addSubview:label];
        _detailTitleLabel = [label retain];
        [label release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"st_cell_arrow.png"] highlightedImage:[UIImage imageNamed:@"st_cell_arrow_hi.png"]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button addSubview:imageView];
        [imageView release];
        CGRect frame = imageView.frame;
        frame.origin.x = (button.bounds.size.width - 26.0f);
        frame.origin.y = (button.bounds.size.height - frame.size.height)/2;
        imageView.frame = frame;
    
    }
    return self;
}

- (void)dealloc {
    self.titleLabel = nil;
    self.detailTitleLabel = nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    CGRect frame = self.titleLabel.frame;
    
    frame.size.width = MIN(frame.size.width, 94.0f);
    if (self.titleLabel.textAlignment == UITextAlignmentRight) {
        frame.origin.x = floorf(100 - frame.size.width);
    } else {
        frame.origin.x = 20.0f;
    }
    
    if (!self.detailTitleLabel.text || self.detailTitleLabel.text.length == 0) {
        frame.size.width = _titleLabel.frame.size.width;
        frame.origin.x = floorf((_titleLabel.superview.bounds.size.width-frame.size.width)/2);
    }
    
    frame.origin.y = floorf((44.0f-frame.size.height)/2);
    self.titleLabel.frame = frame;
    
    [self.detailTitleLabel sizeToFit];
    frame = self.detailTitleLabel.frame;
    frame.origin.x = CGRectGetMaxX(self.titleLabel.frame) + 20.0f;
    frame.size.width = MIN(frame.size.width, self.bounds.size.width - (frame.origin.x + 20.0f));
    frame.origin.y = floorf((44.0f-frame.size.height)/2);
    self.detailTitleLabel.frame = frame;
    
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stButtonTableCellSelected:)]) {
        [self.delegate stButtonTableCellSelected:self];
    }
    
}

@end
