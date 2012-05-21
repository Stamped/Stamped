//
//  LeftMenuTableCell.m
//  Stamped
//
//  Created by Devin Doty on 5/21/12.
//
//

#import "LeftMenuTableCell.h"
#import "STBlockUIView.h"

@implementation LeftMenuTableCell

@synthesize badgeCount=_badgeCount;
@synthesize titleLabel=_titleLabel;
@synthesize border=_border;
@synthesize topBorder=_topBorder;
@synthesize delegate;


- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIFont *font = [UIFont boldSystemFontOfSize:16];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(18.0f, floorf((self.bounds.size.height - font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.backgroundColor = [UIColor clearColor];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.font = font;
        label.textColor = [UIColor colorWithRed:0.765f green:0.765f blue:0.765f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.highlightedTextColor = [UIColor whiteColor];
        label.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.2];
        [self addSubview:label];
        _titleLabel = [label retain];
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
    [_titleLabel sizeToFit];
}


#pragma mark - Setters

- (void)showHighligtedView:(BOOL)show {
    
    self.titleLabel.highlighted = show;
    self.layer.zPosition = show ? 10 : 0;
    [self.layer setValue:[NSNumber numberWithFloat:show ? -2.0f : 0.0f] forKeyPath:@"sublayerTransform.translation.y"];
    
    if ([(id)delegate respondsToSelector:@selector(leftMenuTableCellHighlighted:)]) {
        [self.delegate leftMenuTableCellHighlighted:self];
    }

    if (show) {
        if (!_selectedView) {
            
            UIImage *image = [UIImage imageNamed:@"left_cell_highlight.png"];
            UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
            
            CGRect frame = imageView.frame;
            frame.origin.y = - 6.0f;
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
    [self showHighligtedView:highlighted];
    self.titleLabel.highlighted = highlighted;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    if (_badgeView) {
        [_badgeView setNeedsDisplay];
    }
    [self showHighligtedView:selected];
    
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
            
        }
        
        CGSize size = [[NSString stringWithFormat:@"%i", _badgeCount] sizeWithFont:[UIFont boldSystemFontOfSize:12]];
        CGRect frame = _badgeView.frame;
        frame.size.width = floorf(size.width + 16.0f);
        frame.size.height = 20.0f;
        frame.origin.x = floorf(self.bounds.size.width - (frame.size.width+58.0f));
        frame.origin.y = floorf((self.bounds.size.height-frame.size.height)/2);
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
        view.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.1f];
        view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin;
        [self insertSubview:view atIndex:0];
        [view release];
        
    }
    
    
}

- (void)setTopBorder:(BOOL)border {
    _topBorder = border;
    
    if (_topBorder) {
        
        UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 1.0f)];
        view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.1f];
        view.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        [self insertSubview:view atIndex:0];
        [view release];
        
        view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, self.bounds.size.width, 1.0f)];
        view.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.1f];
        view.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        [self insertSubview:view atIndex:0];
        [view release];
        
    }
    
    
}

@end
