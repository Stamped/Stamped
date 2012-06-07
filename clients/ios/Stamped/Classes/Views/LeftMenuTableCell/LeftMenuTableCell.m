//
//  LeftMenuTableCell.m
//  Stamped
//
//  Created by Devin Doty on 5/21/12.
//
//

#import "LeftMenuTableCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"

@implementation LeftMenuTableCell

@synthesize badgeCount=_badgeCount;
@synthesize titleLabel=_titleLabel;
@synthesize icon=_icon;
@synthesize border=_border;
@synthesize delegate;


- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIFont *font = [UIFont boldSystemFontOfSize:15];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(48.0f, floorf((self.bounds.size.height - font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.backgroundColor = [UIColor clearColor];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.font = font;
        label.textColor = [UIColor colorWithRed:0.690f green:0.690f blue:0.690f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.highlightedTextColor = [UIColor whiteColor];
        label.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.3];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(10.0f, floorf((self.bounds.size.height-30.0f)/2), 30.0f, 30.0f)];
        view.backgroundColor = [UIColor clearColor];
        view.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
           
            if (_icon) {
                
                // flip context
                CGContextTranslateCTM(ctx, 0, rect.size.height);
                CGContextScaleCTM(ctx, 1.0, -1.0);
                
                CGRect fillRect = CGRectMake(ceilf(rect.origin.x + ((rect.size.width-_icon.size.width)/2)), ceilf(rect.origin.y + ((rect.size.height-_icon.size.height)/2)), _icon.size.width, _icon.size.height);

                // draw shadow
                CGContextSaveGState(ctx);
                [[UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.2f] setFill];
                CGContextTranslateCTM(ctx, 0, 1.0f);
                CGContextClipToMask(ctx, fillRect, _icon.CGImage);
                CGContextFillRect(ctx, fillRect);
                CGContextRestoreGState(ctx);
                 
                if (self.highlighted || self.selected) {
                    [[UIColor whiteColor] setFill];
                } else {
                    [[UIColor colorWithRed:0.498f green:0.498f blue:0.498f alpha:1.0f] setFill];
                }
                
                // draw icon
                CGContextClipToMask(ctx, fillRect, _icon.CGImage);
                CGContextFillRect(ctx, fillRect);
                
            }
            
        }];
        _iconView = view;
        [view release];
        
    }
    return self;
}

- (void)dealloc {
    [_icon release], _icon=nil;
    [_titleLabel release], _titleLabel=nil;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [_titleLabel sizeToFit];
}


#pragma mark - Setters

- (void)setIcon:(UIImage *)icon {
    if (_icon) {
        [_icon release], _icon=nil;
    }
    if (icon) {
        _icon = [icon retain];
    }
    [_iconView setNeedsDisplay];
}

- (void)showHighlightedView:(BOOL)show {
    if (self.selectionStyle != UITableViewCellSelectionStyleNone) return;

    if (show) {
        if (!_highlightedView) {
            
            STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:self.bounds];
            view.alpha = 0.6f;
            [self insertSubview:view belowSubview:self.titleLabel];
            [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
                
                drawGradient([UIColor colorWithRed:0.3f green:0.3f blue:0.3f alpha:1.0f].CGColor, [UIColor colorWithRed:0.1f green:0.1f blue:0.1f alpha:1.0f].CGColor, ctx);
                
            }];
            [view release];
            _highlightedView = view;
            
        } 
    } else {
        if (_highlightedView) {
            [_highlightedView removeFromSuperview], _highlightedView=nil;
        }
    }
}

- (void)showSelectedView:(BOOL)show {
    if (self.selectionStyle != UITableViewCellSelectionStyleNone) return;
    
    self.titleLabel.highlighted = show;
    self.layer.zPosition = show ? 10 : 0;
   // [self.layer setValue:[NSNumber numberWithFloat:show ? -2.0f : 0.0f] forKeyPath:@"sublayerTransform.translation.y"];
    
    if ([(id)delegate respondsToSelector:@selector(leftMenuTableCellHighlighted:)]) {
        [self.delegate leftMenuTableCellHighlighted:self];
    }

    if (show) {
        if (!_selectedView) {
            
            UIImage *image = [UIImage imageNamed:@"left_cell_highlight.png"];
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
            
            CGRect frame = imageView.frame;
            frame.origin.y = - 5.0f;
            frame.size.width = self.bounds.size.width;
            [self insertSubview:imageView belowSubview:self.titleLabel];
            imageView.frame = frame;
            [imageView release];
            _selectedView = imageView;
            
        } 
    } else {
        if (_selectedView) {
            [_selectedView removeFromSuperview], _selectedView=nil;
        }
    }
    
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    if (_badgeView) {
        [_badgeView setNeedsDisplay];
    }
    [_iconView setNeedsDisplay];
    [self showHighlightedView:highlighted];
    self.titleLabel.highlighted = highlighted;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    if (_badgeView) {
        [_badgeView setNeedsDisplay];
    }
    [_iconView setNeedsDisplay];
    [self showSelectedView:selected];
    
}

- (void)setBadgeCount:(NSInteger)badgeCount {
    _badgeCount = badgeCount;
    
    if (_badgeCount > 0) {
        
        if (!_badgeView) {
            
            STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectZero];
            view.backgroundColor = [UIColor clearColor];
            [self addSubview:view];
            [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
                
                rect.size.height -= 1.0f; // shadow inset
                CGContextAddPath(ctx, [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:self.bounds.size.height/2].CGPath);
                
                if ([self isHighlighted] || [self isSelected]) {

                    [[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f] setFill];
                    CGContextFillPath(ctx);                    
                    CGContextSetBlendMode(ctx, kCGBlendModeClear);

                } else {
                    
                    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 0.0f, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.1f].CGColor);
                    [[UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.4f] setFill];
                    CGContextFillPath(ctx);
                    
                    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 0.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.4f].CGColor);
                    [[UIColor colorWithRed:0.765f green:0.765f blue:0.765f alpha:1.0f] setFill];
                    
                }
                
                rect.origin.y += 2.0f;
                NSString *title = [NSString stringWithFormat:@"%i", _badgeCount];
                [title drawInRect:rect withFont:[UIFont boldSystemFontOfSize:12] lineBreakMode:UILineBreakModeClip alignment:UITextAlignmentCenter];
                
            }];
            _badgeView = view;
            [view release];
            
        }
        
        CGSize size = [[NSString stringWithFormat:@"%i", _badgeCount] sizeWithFont:[UIFont boldSystemFontOfSize:12]];
        CGRect frame = _badgeView.frame;
        frame.size.width = floorf(size.width + 16.0f);
        frame.size.height = 20.0f;
        frame.origin.x = floorf(self.bounds.size.width - (frame.size.width+58.0f));
        frame.origin.y = floorf(((self.bounds.size.height-frame.size.height)/2) + 2.0f);
        _badgeView.frame = frame;
        [_badgeView setNeedsDisplay];

    } else {
        
        if (_badgeView) {
            [_badgeView removeFromSuperview], _badgeView = nil;
        }
        
    }
    
    
}

- (void)setBorder:(BOOL)border {
    _border = border;
    
    if (_border) {
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height - 2.0f, self.bounds.size.width, 1.0f)];
        view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
        view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;
        [self insertSubview:view atIndex:0];
        [view release];
        
        view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height - 1.0f, self.bounds.size.width, 1.0f)];
        view.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.05f];
        view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;
        [self insertSubview:view atIndex:0];
        [view release];
        
    }
    
    
}

- (void)setTop:(BOOL)top bottom:(BOOL)bottom {
    
    if (top) {
        
        if (!_topBorder) {
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 1.0f)];
            view.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.05f];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
            [self insertSubview:view atIndex:0];
            [view release];
            _topBorder = view;
        }
        
    } else {
        
        if (_topBorder) {
            [_topBorder removeFromSuperview], _topBorder=nil;
        }
        
    }
    
    if (bottom) {
        
        if (!_bottomBorder) {
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-1.0f, self.bounds.size.width, 1.0f)];
            view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
            [self insertSubview:view atIndex:0];
            [view release];
            _bottomBorder = view;
        }
        
    } else {
        
        if (_bottomBorder) {
            [_bottomBorder removeFromSuperview], _bottomBorder = nil;
        }
        
    }
    
    
}


#pragma mark - Notifications 

- (void)countUpdated:(NSNotification*)notification {
    if (![notification object]) return;
    [self setBadgeCount:[[notification object] integerValue]];
}

@end
