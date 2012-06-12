//
//  STDescriptionTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/11/12.
//
//

#import "STDescriptionTableCell.h"

@implementation STDescriptionTableCell
@synthesize detailTitleLabel=_detailTitleLabel;
@synthesize expanded=_expanded;
@synthesize delegate;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if (self = [super initWithStyle:style reuseIdentifier:reuseIdentifier]) {
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [self addSubview:button];
        [button sizeToFit];
        [button setTitleColor:self.titleLabel.textColor forState:UIControlStateNormal];
        button.titleLabel.font = [UIFont systemFontOfSize:11];
        button.contentHorizontalAlignment = UIControlContentHorizontalAlignmentLeft;
        button.hidden = YES;
        _readMoreButton = button;
        
        self.titleLabel.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin;
        CGRect frame = self.titleLabel.frame;
        frame.origin.y = 10.0f;
        self.titleLabel.frame = frame;
        UIFont *font = [UIFont systemFontOfSize:11];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(30.0f, 30.0f, 0.0f, font.lineHeight)];
        label.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor clearColor];
        label.lineBreakMode = UILineBreakModeTailTruncation;
        [self addSubview:label];
        _detailTitleLabel = [label retain];
        [label release];
        
        self.expanded = NO;
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    CGSize size = [self.detailTitleLabel.text sizeWithFont:self.detailTitleLabel.font constrainedToSize:CGSizeMake(self.bounds.size.width - 60.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
    CGRect frame = self.detailTitleLabel.frame;
    frame.size = size;
    _readMoreButton.hidden = ceilf(frame.size.height/self.detailTitleLabel.font.lineHeight) <= 2;
    if (!_expanded) {
        frame.size.height = MIN(self.detailTitleLabel.font.lineHeight*2, frame.size.height);
    }
    self.detailTitleLabel.frame = frame;
    self.detailTitleLabel.numberOfLines = ceilf(size.height/self.detailTitleLabel.font.lineHeight);
    
}

- (void)setExpanded:(BOOL)expanded {
    _expanded = expanded;
    
    [_readMoreButton setTitle:!_expanded ? NSLocalizedString(@"read more", @"read more") : NSLocalizedString(@"read less", @"read less") forState:UIControlStateNormal];
    [_readMoreButton sizeToFit];
    
    CGRect frame = _readMoreButton.frame;
    frame.origin.x = 30.0f;
    frame.origin.y = self.bounds.size.height - 26.0f;
    _readMoreButton.frame = frame;
}

+ (CGFloat)heightForText:(NSString*)text expanded:(BOOL)expanded {
    
    CGRect appFrame = [[UIScreen mainScreen] applicationFrame];
    UIFont *font = [UIFont systemFontOfSize:11];
    CGSize size = [text sizeWithFont:font constrainedToSize:CGSizeMake(appFrame.size.width - 60.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
    
    if (size.height / font.lineHeight > 2) {
        
        if (expanded) {
            return size.height + 60.0f;
        }
        return (font.lineHeight * 2) + 60.0f;
        
    }
    
    return size.height + 40.0f;

}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [_readMoreButton setTitleColor:highlighted ? [UIColor whiteColor] : [UIColor blackColor] forState:UIControlStateHighlighted];
    [super setHighlighted:highlighted animated:animated];
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stDescriptionTableCell:didExpand:)]) {
        [self.delegate stDescriptionTableCell:self didExpand:!self.expanded];
    }

}



@end
