//
//  STSingleTableCell.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "STSingleTableCell.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"

@interface STSingleBackgroundView : UIView
@property(nonatomic,assign) BOOL highlighted;
@end

@implementation STSingleTableCell

@synthesize titleLabel;
@synthesize loading=_loading;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {

        STSingleBackgroundView *view = [[STSingleBackgroundView alloc] initWithFrame:self.bounds];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        self.backgroundView = view;
        [view release];
        
        view = [[STSingleBackgroundView alloc] initWithFrame:self.bounds];
        view.highlighted = YES;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        self.selectedBackgroundView = view;
        [view release];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont boldSystemFontOfSize:13];
        label.highlightedTextColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.349f green:0.349f blue:0.349f alpha:1.0f];
        [self addSubview:label];
        self.titleLabel = label;
        [label release];
        
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    CGRect frame = self.titleLabel.frame;
    
    if (self.titleLabel.textAlignment == UITextAlignmentCenter) {
        
        frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
        
    } else {
        
        frame.origin.x = 20.0f;
        
    }
    frame.origin.y = floorf((self.bounds.size.height-frame.size.height)/2);
    self.titleLabel.frame = frame;
    
    
}

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    self.titleLabel.hidden = _loading;
    
    if (_loading) {
        
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
            [self addSubview:view];
            [view startAnimating];
            [view release];
            _activityView = view;
            
            view.frame = CGRectMake((self.bounds.size.width-20.0f)/2, (self.bounds.size.height-20.0f)/2, 20.0f, 20.0f);
            
        }
        
    } else {
        
        if (_activityView) {
            [_activityView removeFromSuperview], _activityView=nil;
        }
        
    }
    
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    [self.backgroundView setNeedsDisplay];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    [self.backgroundView setNeedsDisplay];
}

+ (CGFloat)height {
    
    return 46.0f;
    
}

@end


#pragma mark - STSingleBackgroundView 

@implementation STSingleBackgroundView
@synthesize highlighted;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        self.backgroundColor = [UIColor clearColor];
    }
    return self;
    
}

- (void)drawRect:(CGRect)rect {
    
    rect = CGRectInset(rect, 10.0f, 3.0f);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:rect cornerRadius:2].CGPath;
    CGContextAddPath(ctx, path);
    
    CGContextSaveGState(ctx);
    CGContextClip(ctx);
    
    if (highlighted) {
        drawGradient([UIColor colorWithRed:0.004f green:0.514f blue:0.976f alpha:1.0f].CGColor, [UIColor colorWithRed:0.129f green:0.286f blue:0.918f alpha:1.0f].CGColor, ctx);
    } else {
        drawGradient([UIColor colorWithRed:0.9921f green:0.9921f blue:0.9921f alpha:1.0f].CGColor, [UIColor colorWithRed:0.9529f green:0.9529f blue:0.9529f alpha:1.0f].CGColor, ctx);
    }
    
    CGContextRestoreGState(ctx);
    
    CGContextSetShadowWithColor(ctx, CGSizeMake(0.0f, 1.0f), 2.0f, [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.05f].CGColor);
    [[UIColor colorWithRed:0.862f green:0.862f blue:0.862f alpha:1.0f] setStroke];
    CGContextAddPath(ctx, path);
    CGContextStrokePath(ctx);
    
    // draw gradient stroke
    if (!highlighted) {

        CGContextAddPath(ctx, path);
        CGContextReplacePathWithStrokedPath(ctx);
        CGContextClip(ctx);
        drawGradient([UIColor colorWithRed:0.886f green:0.886f blue:0.886f alpha:1.0f].CGColor, [UIColor colorWithRed:0.862f green:0.862f blue:0.862f alpha:1.0f].CGColor, ctx);

    } 
     

    
}

@end
