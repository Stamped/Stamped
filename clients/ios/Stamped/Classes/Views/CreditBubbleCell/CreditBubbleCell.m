//
//  CreditBubbleCell.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "CreditBubbleCell.h"

#define kDefaultCellHeight 28.0f
#define kCellBuffer 34.0f

@implementation CreditBubbleCell
@synthesize titleLabel=_titleLabel;
@synthesize stampView=_stampView;

- (id)initWithFrame:(CGRect)frame {
    frame.size.height = kDefaultCellHeight;
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        UIImage *image = [UIImage imageNamed:@"credit_picker_bubble_bg.png"];
        UIImage *imageHi = [UIImage imageNamed:@"credit_picker_bubble_bg_hi.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] highlightedImage:[imageHi stretchableImageWithLeftCapWidth:(imageHi.size.width/2) topCapHeight:0]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        CGRect frame = imageView.frame;
        frame.origin.y = floorf((self.bounds.size.height-frame.size.height)/2);
        frame.size.width = self.bounds.size.width;
        imageView.frame = frame;
        [self addSubview:imageView];
        [imageView release];
        _background = imageView;
        
        UserStampView *view = [[UserStampView alloc] initWithFrame:CGRectMake(6.0f, floorf((self.bounds.size.height-14.0f)/2), 14.0f, 14.0f)];
        [self addSubview:view];
        _stampView = [view retain];
        [view release];
        
        UIFont *font = [UIFont boldSystemFontOfSize:11];
        CGFloat originY = floorf(((self.bounds.size.height-font.lineHeight)/2));
        CGFloat originX = floorf(CGRectGetMaxX(_stampView.frame) + 4.0f);
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(originX, originY, 0.0f, font.lineHeight)];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.shadowColor = [UIColor colorWithWhite:1.0f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        label.backgroundColor = [UIColor clearColor];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];

    }
    return self;
}

- (void)dealloc {
    [_stampView release], _stampView=nil;
    [_titleLabel release], _titleLabel=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [_titleLabel sizeToFit];
}

- (CGSize)sizeThatFits:(CGSize)size {
    
    [_titleLabel sizeToFit];
    return CGSizeMake(_titleLabel.bounds.size.width + kCellBuffer, kDefaultCellHeight);
    
}

- (void)deselect {
    self.selected = NO;
}

- (void)adjustHighlight:(BOOL)highlighted {
    
    if (self.selected) {
        highlighted = YES;
    }
    
    _titleLabel.highlighted = highlighted;
    _titleLabel.shadowOffset = CGSizeMake(0.0f, highlighted ? 0.0f : -1.0f);
    _stampView.highlighted = highlighted;
    _background.highlighted = highlighted;
    
}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    [self adjustHighlight:selected];
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [self adjustHighlight:highlighted];
}


@end
