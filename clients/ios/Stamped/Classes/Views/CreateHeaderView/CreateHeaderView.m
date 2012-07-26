//
//  CreateHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/13/12.
//
//

#import "CreateHeaderView.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "Util.h"

@implementation CreateHeaderView

@synthesize titleLabel = _titleLabel;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        CGFloat insent = 16.0f;

        UIFont *font = [UIFont stampedTitleFontWithSize:26];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(insent, 14.0f, 0.0f, font.lineHeight)];
        label.backgroundColor = self.backgroundColor;
        label.font = font;
        label.textColor = [UIColor stampedBlackColor];
        label.highlightedTextColor = [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f];
        [self addSubview:label];
        _titleLabel = label;
        [label release];
        
        font = [UIFont systemFontOfSize:11];
        label = [[UILabel alloc] initWithFrame:CGRectMake(32.0f, CGRectGetMaxY(_titleLabel.frame) - 2.0f, 0.0f, font.lineHeight)];
        label.backgroundColor = self.backgroundColor;
        label.font = font;
        label.textColor = [UIColor stampedGrayColor];
        label.highlightedTextColor = [UIColor colorWithRed:0.651f green:0.651f blue:0.651f alpha:1.0f];
        [self addSubview:label];
        _detailTitleLabel = label;
        [label release];
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(insent, _detailTitleLabel.frame.origin.y + 2.0f, 30.0f, 30.0f)];
        [self addSubview:imageView];
        _imageView = imageView;
        [imageView release];
        
        UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"st_cell_arrow_large.png"]];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        
        CGRect frame = view.frame;
        frame.origin.x = (self.bounds.size.width - (frame.size.width+insent));
        frame.origin.y = (self.bounds.size.height - frame.size.height)/2;
        view.frame = frame;
        [view release];  
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];

    [_titleLabel sizeToFit];
    [_detailTitleLabel sizeToFit];
    [_imageView sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width -58.0f, frame.size.width);
    _titleLabel.frame = frame;
    
    frame = _detailTitleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width -58.0f, frame.size.width);
    _detailTitleLabel.frame = frame;
    
}

- (void)setupWithItem:(id)item {
    _titleLabel.text = [item title];
    _detailTitleLabel.text = [item subtitle];
    UIImage* rawImage = [Util categoryIconForCategory:[item category] subcategory:nil filter:nil andSize:STCategoryIconSize9];
    _imageView.image = [Util gradientImage:rawImage withPrimaryColor:@"b2b2b2" secondary:@"b2b2b2" andStyle:STGradientStyleVertical];
    [self setNeedsLayout];

}

- (void)adjustHighlight {
    
    BOOL highlighted = (self.selected || self.highlighted);
    self.backgroundColor = highlighted ? [UIColor colorWithWhite:0.0f alpha:0.05f] : [UIColor clearColor];
    
    for (UIView *view in self.subviews) {
    
        if ([view respondsToSelector:@selector(setHighlighted:)]) {
            [(id)view setHighlighted:highlighted];
        }
    
    }

}

- (void)setSelected:(BOOL)selected {
    [super setSelected:selected];
    [self adjustHighlight];
}

- (void)setHighlighted:(BOOL)highlighted {
    [super setHighlighted:highlighted];
    [self adjustHighlight];
}

@end
