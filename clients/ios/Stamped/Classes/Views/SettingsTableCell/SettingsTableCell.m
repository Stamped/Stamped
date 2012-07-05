//
//  SettingsTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import "SettingsTableCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"

@implementation SettingsTableCell
@synthesize titleLabel=_titleLabel;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if (self = [super initWithStyle:style reuseIdentifier:reuseIdentifier]) {
        
        self.backgroundView = [[[UIView alloc] initWithFrame:CGRectZero] autorelease];

        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 0.0f)];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        background.backgroundColor = [UIColor clearColor];
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            
            CGFloat inset = 8.5f;
            CGFloat corner = 2.0f;
            
            UIColor *topColor = [UIColor colorWithRed:0.019f green:0.545f blue:0.96f alpha:1.0f];
            UIColor *bottomColor = [UIColor colorWithRed:0.0039f green:0.364f blue:0.901f alpha:1.0f];
            
            CGPathRef path;
            
            if (_topBorder && _bottomBorder) {
                
                path = [UIBezierPath bezierPathWithRect:CGRectInset(rect, inset, 0)].CGPath;
                
            } else if (_topBorder) {
                
                path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, inset, 0) byRoundingCorners:(UIRectCornerTopLeft | UIRectCornerTopRight) cornerRadii:CGSizeMake(corner, corner)].CGPath;
                
            } else if (_bottomBorder) {
                
                path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, inset, 0) byRoundingCorners:(UIRectCornerBottomLeft | UIRectCornerBottomRight) cornerRadii:CGSizeMake(corner, corner)].CGPath;
                
            } else {
                
                path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, inset, 0) cornerRadius:corner].CGPath;
                
            }
            
            CGContextAddPath(ctx, path);
            CGContextClip(ctx);
            drawGradient(topColor.CGColor, bottomColor.CGColor, ctx);
            
        }];
        
        self.selectedBackgroundView = background;
        [background release];
        
        UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"st_cell_arrow.png"] highlightedImage:[UIImage imageNamed:@"st_cell_arrow_hi.png"]];
        view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [self addSubview:view];
        [view release];
        CGRect frame = view.frame;
        frame.origin.x = (self.bounds.size.width - 36.0f);
        frame.origin.y = (self.bounds.size.height - frame.size.height)/2;
        view.frame = frame;
        
        UIFont *font = [UIFont boldSystemFontOfSize:11];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(30.0f, floorf((self.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.textColor = [UIColor colorWithWhite:0.349f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor clearColor];
        [self addSubview:label];
        self.titleLabel = label;
        [label release];
        
    
    }
    return self;
}

- (void)dealloc {
    [_titleLabel release], _titleLabel=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [self.titleLabel sizeToFit];
}

- (void)prepareForReuse {
    [super prepareForReuse];
    
    if (_background.superview!=self) {
        [self addSubview:_background];
    }
    
}


#pragma mark - Setters

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    
    if (selected) {
        [self.selectedBackgroundView setNeedsDisplay];
    }
    
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    
    if (highlighted) {
        [self.selectedBackgroundView setNeedsDisplay];
    }
    
}

- (void)setFirst:(BOOL)first last:(BOOL)last {
            
    if (!last) {
        if (!_topBorder) {
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(18.5f, self.bounds.size.height-1.0f, self.bounds.size.width-37.0f, 1.0f)];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
            [self addSubview:view];
            view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
            _topBorder = view;
            [view release];
        }
    } else {
        if (_topBorder) {
            [_topBorder removeFromSuperview], _topBorder=nil;
        }
    }
    
    if (!first) {
        if (!_bottomBorder) {
            
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(18.5f, 0.0f, self.bounds.size.width-37.0f, 1.0f)];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
            view.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.4f];
            [self addSubview:view];
            _bottomBorder = view;
            [view release];
            
        }
    } else {
        if (_bottomBorder) {
            [_bottomBorder removeFromSuperview], _bottomBorder=nil;
        }
    }
    
    
}


@end
