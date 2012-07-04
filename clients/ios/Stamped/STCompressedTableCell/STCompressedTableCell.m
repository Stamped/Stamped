//
//  STCompressedTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/25/12.
//
//

#import "STCompressedTableCell.h"

@implementation STCompressedTableCell
@synthesize titleLabel=_titleLabel;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {

        self.backgroundView = [[[UIView alloc] init] autorelease];
        self.selectionStyle = UITableViewCellSelectionStyleNone;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.highlightedTextColor = [UIColor whiteColor];
        label.backgroundColor = [UIColor clearColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.shadowColor = [UIColor whiteColor];
        label.font = [UIFont systemFontOfSize:12];
        label.textColor = [UIColor colorWithRed:0.478f green:0.611f blue:0.8f alpha:1.0f];
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
    CGRect frame = _titleLabel.frame;
    frame.origin.x = floorf((self.bounds.size.width-frame.size.width)/2);
    frame.origin.y = floorf((self.bounds.size.height-frame.size.height)/2);
    _titleLabel.frame = frame;
    
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
}

@end
