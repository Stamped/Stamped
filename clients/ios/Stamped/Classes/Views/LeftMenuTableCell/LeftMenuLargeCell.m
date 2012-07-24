//
//  LeftMenuLargeCell.m
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "LeftMenuLargeCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STUnreadActivity.h"
#import "UIFont+Stamped.h"
#import "Util.h"

static const CGFloat _cellHeight = 72;

@implementation LeftMenuLargeCell

@synthesize titleLabel=_titleLabel;
@synthesize icon=_icon;
@synthesize border=_border;
@synthesize delegate;


- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIFont *font = [UIFont stampedTitleLightFontWithSize:40];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(14, 18 + floorf((self.bounds.size.height - font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.backgroundColor = [UIColor clearColor];
        label.font = font;
        label.textColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.highlightedTextColor = [UIColor whiteColor];
        label.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.3];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        [_titleLabel addObserver:self forKeyPath:@"text" options:0 context:nil];
        STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(0, 0.0f, 300, _cellHeight)];
        view.backgroundColor = [UIColor clearColor];
        view.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            if (_icon) {
                
                // flip context
                CGContextTranslateCTM(ctx, 0, rect.size.height);
                CGContextScaleCTM(ctx, 1.0, -1.0);
                
                CGRect fillRect = CGRectMake(CGRectGetMaxX(self.titleLabel.frame), _cellHeight - 28, _icon.size.width, _icon.size.height);
                //HACK
                if ([self.titleLabel.text isEqualToString:@"The Guide"]) {
                    fillRect = CGRectOffset(fillRect, -4, -4);
                }
                
                CGContextSaveGState(ctx);
                CGContextSetFillColorWithColor(ctx, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.2f].CGColor);
                CGContextTranslateCTM(ctx, 0, 1.0f);
                CGContextClipToMask(ctx, fillRect, _icon.CGImage);
                CGContextFillRect(ctx, fillRect);
                CGContextRestoreGState(ctx);
                // draw shadow
                
                if (self.highlighted || self.selected) {
                    
                    [[UIColor whiteColor] setFill];
                    CGContextClipToMask(ctx, fillRect, _icon.CGImage);
                    CGContextClearRect(ctx, fillRect);
                    CGContextFillRect(ctx, fillRect);
                    
                } 
                else {
                    CGContextDrawImage(ctx, fillRect, _icon.CGImage);
                    //                    [[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.2f] setFill];
                }
                
                // draw icon
                
            }
            
        }];
        _iconView = view;
        [view release];
    }
    return self;
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context {
    if ([keyPath isEqualToString:@"text"]) {
        [self.titleLabel sizeToFit];
    }
    else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

- (void)dealloc {
    [_icon release], _icon=nil;
    [_titleLabel removeObserver:self forKeyPath:@"text"];
    [_titleLabel release], _titleLabel=nil;
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
            [view setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
                
                drawGradient([UIColor colorWithRed:0 green:0 blue:0 alpha:1.0f].CGColor, [UIColor colorWithRed:0 green:0 blue:0 alpha:1.0f].CGColor, ctx);
                
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
    
    if ([(id)delegate respondsToSelector:@selector(leftMenuTableCellHighlighted:highlighted:)]) {
        [self.delegate leftMenuTableCellHighlighted:self highlighted:self.highlighted];
    }
    
    if (show) {
        if (!_selectedView) {
            
            UIImage *image = [UIImage imageNamed:@"left_cell_highlight.png"];
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
            
            CGRect frame = imageView.frame;
            frame.origin.y = - 10.0f;
            frame.size.height += 34;
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
    [_iconView setNeedsDisplay];
    [self showHighlightedView:highlighted];
    self.titleLabel.highlighted = highlighted;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    [_iconView setNeedsDisplay];
    [self showSelectedView:selected];
    
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

@end
